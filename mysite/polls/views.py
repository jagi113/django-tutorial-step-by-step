from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.views import generic
from django.utils import timezone
import datetime
import pandas as pd
from django_pandas.io import read_frame

from .models import Choice, Question, Votes


class IndexView(generic.ListView):
    template_name = 'polls/index.html'
    context_object_name = 'latest_question_list'

    def get_queryset(self):
        """
        Return the last five published questions (not including those set to be
        published in the future).
        """
        return Question.objects.filter(
            pub_date__lte=timezone.now()
        ).order_by('-pub_date')[:5]


class DetailView(generic.DetailView):
    model = Question
    template_name = 'polls/detail.html'

    def get_queryset(self):
        """
        Excludes any questions that aren't published yet.
        """
        return Question.objects.filter(pub_date__lte=timezone.now())

    # Added function for retrieving votes and passing to template as context
    def get_context_data(self, **kwargs):
        context = super(DetailView, self).get_context_data(**kwargs)
        try:
            votes_context = getPdVotes(
                pk=self.kwargs['pk'], order=self.kwargs['order'], url='')
            context.update(votes_context)
            return context
        except:
            return context


class ResultsView(generic.DetailView):
    model = Question
    template_name = 'polls/results.html'

    # Added function for retrieving votes and passing to template as context
    def get_context_data(self, **kwargs):
        context = super(ResultsView, self).get_context_data(**kwargs)
        try:
            votes_context = getPdVotes(
                pk=self.kwargs['pk'], order=self.kwargs['order'], url='results/')
            context.update(votes_context)
            return context
        except:
            return context


def vote(request, question_id, order):
    question = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = question.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        # Redisplay the question voting form.
        return render(request, 'polls/detail.html', {
            'question': question,
            'error_message': "You didn't select a choice.",
        })
    else:
        selected_choice.votes += 1
        selected_choice.save()

        # Added functionality for saving a vote
        vote_time = floor_dt(datetime.datetime.now() +
                             datetime.timedelta(hours=1), 1)
        vote = Votes(question=question, choice=selected_choice,
                     vote_time=vote_time)
        vote.save()

        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.
        return HttpResponseRedirect(reverse('polls:results', args=(question.id, order)))


# - function getPdVotes presents table of votes in pandas dataframe converted to HTML
# - function getPdVotes is called within DetailView and ResultsView classes (views.py)
# - function loads all votes for needed question, parses all saved choices and times of votes
# - for each loaded row it creates a new dataset row with:
#      time key and value of vote time
#      key for each case of saved choice (alphabeticaly ordered) - for each choice value equal to vote it adds +1
#      - if time value of the following row is the same as time value of previous one, it does not create a new dataset row but modifies values of choices of the same dataset row
# - keys for each values are links, so table is possible to order by clicking on column-headers
def getPdVotes(url, pk=1, order='Time'):
    item = Votes.objects.filter(question_id=pk)
    df = read_frame(item, fieldnames=['vote_time', 'choice'])
    choices = pd.Series(df['choice']).drop_duplicates().tolist()
    all_votes = []
    for _, time, vote in df.itertuples():
        vote_info = {make_clickable(
            pk, 'Time', url): time.strftime("%y/%m/%d  %H:%M")}
        for choice in choices:
            if vote == choice:
                vote_info[make_clickable(pk, choice, url)] = 1
            else:
                vote_info[make_clickable(pk, choice, url)] = 0
        all_votes.append(vote_info)
    votes = pd.DataFrame(
        all_votes, index=[i for i in range(len(all_votes))])
    grouped_votes = votes.groupby(
        votes[f"<a href='/polls/{pk}/{url}Time/'>Time</a>"]).sum()
    sorted_votes = grouped_votes.sort_values(
        by=[f"<a href='/polls/{pk}/{url}{order}/'>{order}</a>"], ascending=False)
    mydict = {
        "df": sorted_votes.to_html(escape=False).replace('<td>', '<td align="center">'),
    }
    return mydict


# function to round time of vote to minutes
def floor_dt(dt, interval):
    replace = (dt.minute // interval)*interval
    return dt.replace(minute=replace, second=0, microsecond=0)


# function to create headers with url sorting
def make_clickable(pk, val, url):
    return f"<a href='/polls/{pk}/{url}{val}/'>{val}</a>"

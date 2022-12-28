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
        try:
            votes_context = getVotes(pk=self.kwargs['pk'])
            return votes_context
        except:
            return Question.objects.filter(pub_date__lte=timezone.now())


class ResultsView(generic.DetailView):
    model = Question
    template_name = 'polls/results.html'

    # Added function for retrieving votes and passing to template as context

    def get_context_data(self, **kwargs):
        votes_context = getVotes(pk=self.kwargs['pk'])
        return votes_context


def vote(request, question_id):
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
        return HttpResponseRedirect(reverse('polls:results', args=(question.id, )))


# Solution 1 - shows in results.html using template in inclueds/table.html
# function for retrieving votes objects, parsing and creating context for table
def getVotes(pk):
    context = {}
    context["dataset"] = Votes.objects.filter(question_id=pk)
    context["question"] = context["dataset"][0].question
    context["choices"] = set(ch.choice for ch in [
                             v for v in context["dataset"]])
    votes = [{"time": context["dataset"]
              [0].vote_time.strftime("%y/%m/%d, %H:%M")}]
    i = 0
    for vote in context["dataset"]:
        if votes[i]["time"] != vote.vote_time.strftime("%y/%m/%d, %H:%M"):
            i += 1
            votes.append({"time": vote.vote_time.strftime("%y/%m/%d, %H:%M")})
        for choice in context["choices"]:
            if votes[i].get(str(choice)) == None:
                votes[i][str(choice)] = 0
            if choice == vote.choice:
                votes[i][str(choice)] += 1
    context["votes"] = votes
    return context


# Solution 2 - using pandas dataframe with group by functionality
#           - presents in own votes_list.html: path('<int:pk>/votes/<str:order>', views.showVotes, name='votes'),
#           - http://127.0.0.1:8000/polls/1/votes/Time/
def showVotes(request, pk=1, order='Time'):
    try:
        item = Votes.objects.filter(question_id=pk)
        df = read_frame(item, fieldnames=['vote_time', 'choice'])
        choices = pd.Series(df['choice']).drop_duplicates().tolist()
        all_votes = []
        for _, time, vote in df.itertuples():
            vote_info = {make_clickable(
                pk, 'Time'): time.strftime("%y/%m/%d  %H:%M")}
            for choice in choices:
                if vote == choice:
                    vote_info[make_clickable(pk, choice)] = 1
                else:
                    vote_info[make_clickable(pk, choice)] = 0
            all_votes.append(vote_info)
        votes = pd.DataFrame(
            all_votes, index=[i for i in range(len(all_votes))])
        grouped_votes = votes.groupby(
            votes[f"<a href='/polls/{pk}/votes/Time/'>Time</a>"]).sum()

        sorted_votes = grouped_votes.sort_values(
            by=[f"<a href='/polls/{pk}/votes/{order}/'>{order}</a>"], ascending=False)

        mydict = {
            "df": sorted_votes.to_html(escape=False).replace('<td>', '<td align="center">'),
            "question_id": pk,
        }
        return render(request, "polls/votes_list.html", mydict)
    except:
        return render(request, "polls/votes_list.html", context=None)


# function to round time of vote to minutes
def floor_dt(dt, interval):
    replace = (dt.minute // interval)*interval
    return dt.replace(minute=replace, second=0, microsecond=0)


# function to create headers with url sorting
def make_clickable(pk, val):
    return f"<a href='/polls/{pk}/votes/{val}/'>{val}</a>"

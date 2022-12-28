Original project was edited in following manner:

1. Model Votes was added chapturing question, selected choice and time of vote rounded to minutes by default (models.py)

2. An instance of Votes is created and saved in vote function (views.py)

3. First solution - function getVotes presents table of votes in results.html template showing on results path (views.py)

   - function getVotes is called within ResultsView class (views.py)
   - function loads all votes for needed question, parses all saved choices and times of votes
   - for each loaded row it creates a new dataset row with:
     time key and value of vote time
     key for each case of saved choice (alphabeticaly ordered) - for each choice value equal to vote it adds +1 - if time value of the following row is the same as time value of previous one, it does not create a new dataset row but modifies values of choices of the same dataset row
   - new dataset is passed to context under votes key

4. For better functionality (filtering and ordering) I created second solution showVotes using pandas dataframes
   - solution present table using votes_list.html template and can be seen on path('< int:pk>/votes/< str:order>/', views.showVotes, name='votes'),
   - principle of parsing is similar as in first solution
   - interactive ordering is added

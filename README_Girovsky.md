Original project was edited in following manner:

1. Model Votes was added chapturing question, selected choice and time of vote rounded to minutes by default (models.py)

2. An instance of Votes is created and saved in vote function (views.py)

3. Solution to presenting - function getPdVotes presents table of votes in pandas dataframe converted to HTML

   - function getPdVotes is called within DetailView and ResultsView classes (views.py)
   - function loads all votes for needed question, parses all saved choices and times of votes
   - for each loaded row it creates a new dataset row with:
     time key and value of vote time
     key for each case of saved choice (alphabeticaly ordered) - for each choice value equal to vote it adds +1 - if time value of the following row is the same as time value of previous one, it does not create a new dataset row but modifies values of choices of the same dataset row
   - keys for each values are links, so table is possible to order by clicking on column-headers

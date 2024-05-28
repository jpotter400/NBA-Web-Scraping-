#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd 
import requests
pd.set_option("display.max_columns", None) # to be able to see all columns 
import time 
import numpy as np


# In[2]:


test_url = 'https://stats.nba.com/stats/leagueLeaders?LeagueID=00&PerMode=Totals&Scope=S&Season=2012-13&SeasonType=Regular%20Season&StatCategory=PTS'


# In[3]:


r = requests.get(url=test_url).json()


# In[4]:


r


# In[5]:


r['resultSet']


# In[6]:


table_headers = r['resultSet']['headers']


# In[7]:


r['resultSet']['rowSet']
# row set is where the data for indivdual players starts


# In[8]:


r['resultSet']['rowSet'][3]
# im biased so I used my favorite player (:


# In[9]:


pd.DataFrame(r['resultSet']['rowSet'])
# no table headers but thats okat because we have a varaible for that


# In[10]:


pd.DataFrame(r['resultSet']['rowSet'], columns=table_headers)
# added our previsouly maybe table_header to help show which stat goes with the random numbers
# this is also 10 years worth of NBA data 


# In[11]:


temp_df1 = pd.DataFrame(r['resultSet']['rowSet'], columns=table_headers)
temp_df2 = pd.DataFrame({'Year':['2012-13' for i in range(len(temp_df1))], 
                         'Season_type':['Regular%20Season' for i in range(len(temp_df1))]})
temp_df3 = pd.concat([temp_df2,temp_df1], axis=1)


# In[12]:


temp_df2


# In[13]:


temp_df3


# In[14]:


del temp_df1, temp_df2, temp_df3


# In[15]:


df_cols = ['Year', 'Season_type'] + table_headers
# adding to table headers 


# In[16]:


pd.DataFrame(columns=df_cols)
# quick check to make sure its just headers and nothing else


# In[17]:


headers = {
    'Accept': '*/*',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'en-US,en;q=0.9',
    'Connection': 'keep-alive',
    'Host': 'stats.nba.com',
    'Origin': 'https://www.nba.com',
    'Referer': 'https://www.nba.com/',
    'Sec-Ch-Ua': '"Chromium";v="118", "Google Chrome";v="118", "Not=A?Brand";v="99"',
    'Sec-Ch-Ua-Mobile': '?0',
    'Sec-Ch-Ua-Platform': "Windows",
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-site',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36'
}


# In[18]:


df = pd.DataFrame(columns=df_cols)
season_types = ['Regular%20Season', 'Playoffs']
years = ['2012-13', '2013-14', '2014-15', '2015-16', '2016-17', '2017-18', '2018-19', '2019-20', '2020-21', '2021-22', '2022-23']

begin_loop = time.time()

for y in years:
    for s in season_types: 
        api_url ='https://stats.nba.com/stats/leagueLeaders?LeagueID=00&PerMode=Totals&Scope=S&Season='+y+'&SeasonType='+s+'&StatCategory=PTS'
        r = requests.get(url=api_url).json()
        temp_df1 = pd.DataFrame(r['resultSet']['rowSet'], columns=table_headers)
        temp_df2 = pd.DataFrame({'Year':[y for i in range(len(temp_df1))], 
                                 'Season_type':[s for i in range(len(temp_df1))]})
        temp_df3 = pd.concat([temp_df2,temp_df1], axis=1)
        df = pd.concat([df, temp_df3], axis=0)
        print(f'Finished scraping data for the {y} {s}.')
        lag = np.random.uniform(low=5,high=40)
        print(f'...waiting {round(lag,1)} seconds')
        time.sleep(lag)
        
print(f'Process completed: Total run time: {round((time.time()-begin_loop)/60,2)}')

        
        
            
        


# In[19]:


df.sample(10)
# may not need rank, kind of pointless


# ## Data Cleaning & Analysis Prep

# In[20]:


df.isna().sum()
# no null values! 


# In[21]:


df.drop(columns=['RANK'], inplace=True)
# inplace avoids creating a new dataframe with other modifications, just makes changes to the original 


# In[22]:


df['Season_Start_Year'] = df['Year'].str[:4].astype(int)


# In[23]:


df.TEAM.unique()
# The hornets changed to the Pelicans within the years of our timeframe so Im going to standarize that


# In[24]:


df['TEAM'].replace(to_replace=['NOP','NOH'], value='NO', inplace=True)


# In[25]:


df.TEAM.unique()
# fixed


# In[26]:


df['Season_type'].replace('Regular%20Season', 'Rregular Season', inplace=True)


# In[55]:


df.sample(100)


# In[63]:


df[df['Season_type']=='Regular Season']
playoffs_df = df[df['Season_type']=='Regular Season']


# In[29]:


df.columns


# In[30]:


total_cols = ['MIN', 'FGM', 'FGA','FG3M', 'FG3A', 'FTM', 'FTA',
              'OREB', 'DREB', 'REB', 'AST', 'STL', 'BLK', 'TOV', 'PF','PTS']


# ## Which player stats correlate?

# In[31]:


get_ipython().system('pip install plotly')


# In[39]:


import plotly.express as px 
import matplotlib.pyplot as plt


# In[40]:


data_per_min = df.groupby(['PLAYER', 'PLAYER_ID', 'Year'])[total_cols].sum().reset_index()
for col in data_per_min.columns[4:]:
    data_per_min[col] = data_per_min[col]/data_per_min['MIN']
    
    
data_per_min['FG%'] = data_per_min['FGM']/data_per_min['FGA']
data_per_min['3PT%'] = data_per_min['FG3M']/data_per_min['FG3A']
data_per_min['FT%'] = data_per_min['FTM']/data_per_min['FTA']
data_per_min['FG3A%'] = data_per_min['FG3A']/data_per_min['FGA'] #attempts that are 3 pointers 
data_per_min['PTS/FGA'] = data_per_min['PTS']/data_per_min['FGA']
data_per_min['FG3M/FGM'] = data_per_min['FG3M']/data_per_min['FGM']
data_per_min['FTA/FGA'] = data_per_min['FTA']/data_per_min['FGA']
data_per_min['TRU%'] = 0.5*data_per_min['PTS']/(data_per_min['FGA']+0.475*data_per_min['FTA'])
data_per_min['AST_TOV'] = data_per_min['AST']/data_per_min['TOV']

data_per_min = data_per_min[data_per_min['MIN']>=50] # taking out those who didnt play at least 50 minutes
data_per_min.drop(columns='PLAYER_ID', inplace=True)

fig = px.imshow(data_per_min.corr())
fig.show()


# to get an accurate reading I am going to go by minutes played 


# ## How are minutes played distributed? 

# In[50]:


fig = px.histogram(x=data_per_min['MIN'], histnorm='percent')
fig.show()


# In[51]:


fig = px.histogram(x=playoffs_df['MIN'], histnorm='percent')
fig.show()


# ## How the game has changed over the past 10 years

# In[66]:


change_df = df.groupby('Season_Start_Year')[total_cols].sum().reset_index()
change_df
# covid 2019-2020


# In[77]:


import plotly.graph_objects as go


# In[71]:


change_df = df.groupby('Season_Start_Year')[total_cols].sum().reset_index()
change_df['POSS_est'] = change_df['FGA']-change_df['OREB']+change_df['TOV']+0.41*change_df['FTA']
# I am attmepting to get possesions per game for each year.
# with field goals, free throws, turnovers and rebounds being ways to end a possesion this will be skewed because I will never know the real amount 
# also shot clock violation is a team turnover and not a specific player which is also not a stat I have available 
change_df['FG%'] = change_df['FGM']/change_df['FGA']
change_df['3PT%'] = change_df['FG3M']/change_df['FG3A']
change_df['FT%'] = change_df['FTM']/change_df['FTA']
change_df['FG3A%'] = change_df['FG3A']/change_df['FGA'] #attempts that are 3 pointers 
change_df['PTS/FGA'] = change_df['PTS']/change_df['FGA']
change_df['FG3M/FGM'] = change_df['FG3M']/change_df['FGM']
change_df['FTA/FGA'] = change_df['FTA']/change_df['FGA']
change_df['TRU%'] = 0.5*change_df['PTS']/(change_df['FGA']+0.475*change_df['FTA'])
change_df['AST_TOV'] = change_df['AST']/change_df['TOV']

change_df


# In[79]:


change_per48_df = change_df.copy()
for col in change_per48_df.columns[2:18]:
    change_per48_df[col] = (change_per48_df[col]/change_per48_df['MIN'])*48*5

fig = go.Figure()
for col in change_per48_df.columns[1:]:
    fig.add_trace(go.Scatter(x=change_per48_df['Season_Start_Year'],
                            y=change_per48_df[col], name=col))
fig.show()
# per 48 minutes per game and theres always going to be 5 players on the court per team


# In[ ]:


# Turnovers being steady is something that sticks out to me 
# Free throw attempts is also something that sticks out 


# In[ ]:





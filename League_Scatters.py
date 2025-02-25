import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats
from statistics import mean
from math import pi
import streamlit as st
sns.set_style("white")
import warnings
warnings.filterwarnings('ignore')
import matplotlib
import plotly.express as px
import plotly.figure_factory as ff
from plotly.graph_objects import Layout
def click_button():
    st.session_state.clicked = True
def reset_click_button():
    st.session_state.clicked = False

matplotlib.rcParams.update(matplotlib.rcParamsDefault)

st.title('Player Scatter Plot Program')
st.subheader('Created by Ben Griffis (Twitter: @BeGriffis)\nAll data from Wyscout')

with st.expander('Read App Details'):
    st.write('''
    This app allows you to create your own scatter plots to visualize players.
    First, choose a league, position, & minimum minutes threshold.
    These will determine the sample size of players that scatters will generate for.
    Then, use the metric selectors on the side to choose the X and Y variables.
    ''')

lg_lookup = pd.read_csv('https://raw.githubusercontent.com/griffisben/Wyscout_Prospect_Research/main/league_info_lookup.csv')
df = pd.read_csv('https://raw.githubusercontent.com/griffisben/Wyscout_Prospect_Research/main/Japan_Korea_2022_WS.csv')
df = df.dropna(subset=['Position','Team within selected timeframe', 'Age']).reset_index(drop=True)


df['pAdj Tkl+Int per 90'] = df['PAdj Sliding tackles'] + df['PAdj Interceptions']
df['1st, 2nd, 3rd assists'] = df['Assists per 90'] + df['Second assists per 90'] + df['Third assists per 90']
df['1st, 2nd, 3rd assists per 90'] = df['1st, 2nd, 3rd assists'] / (df['Minutes played'] / 90)
df['xA per Shot Assist'] = df['xA per 90'] / df['Shot assists per 90']
df['Aerial duels won per 90'] = df['Aerial duels per 90'] * (df['Aerial duels won, %']/100)
df['Cards per 90'] = df['Yellow cards per 90'] + df['Red cards per 90']
df['Clean sheets, %'] = df['Clean sheets'] / df['Matches played']
df['npxG'] = df['xG'] - (.76 * df['Penalties taken'])
df['npxG per 90'] = df['npxG'] / (df['Minutes played'] / 90)
df['npxG per shot'] = df['npxG'] / (df['Shots'] - df['Penalties taken'])

df = df.dropna(subset=['Position', 'Team within selected timeframe', 'Age']).reset_index(drop=True)
df.rename(columns={'Team':'xxxTeam', 'Team within selected timeframe':'Team'})

df['Main Position'] = ''
for i in range(len(df)):
    df['Main Position'][i] = df['Position'][i].split()[0]


with st.sidebar:
    st.header('Choose Basic Options')
    league = st.selectbox('League', (lg_lookup.League.tolist()))
    pos = st.selectbox('Positions', ('Strikers', 'Strikers and Wingers', 'Forwards (AM, W, CF)',
                                    'Forwards no ST (AM, W)', 'Wingers', 'Midfielders (DM, CM, CAM)',
                                    'Central & Defensive Midfielders (DM, CM)', 'Central & Attacking Midfielders (CM, CAM)', 'Fullbacks (FBs/WBs)',
                                    'Defenders (CB, FB/WB, DM)', 'Centre-Backs', 'Goalkeepers'))
    mins = st.number_input('Minimum Minutes Played', 400, max(df['Minutes played'].astype(int)), 900)
    xx = st.selectbox('X-Axis', (df.columns[5:len(df.columns)].tolist()))
    yy = st.selectbox('Y-Axis', (df.columns[5:len(df.columns)].tolist()))
    cc = st.selectbox('Point Color', (df.columns[5:len(df.columns)].tolist()))
    flipX = xx
    flipY = yy
    
    if 'clicked' not in st.session_state:
        st.session_state.clicked = False
    st.button('Swap X & Y Axes', on_click=click_button)
    if st.session_state.clicked:
        xx = flipY
        yy = flipX
    if 'clicked' not in st.session_state:
        st.session_state.clicked = False
    st.button('Swap X & Y Axes Back', on_click=reset_click_button)
        

ssn = lg_lookup[lg_lookup['League']==league].Season.values[0]
date = lg_lookup[lg_lookup['League']==league].Date.values[0]
    
# Filter data
dfProspect = df[(df['Minutes played']>=mins) & (df['League']==league)].copy()


if pos == 'Forwards (AM, W, CF)':
    dfProspect = dfProspect[(dfProspect['Main Position'].str.contains('CF')) |
                           (dfProspect['Main Position'].str.contains('RW')) |
                           (dfProspect['Main Position'].str.contains('LW')) |
                           (dfProspect['Main Position'].str.contains('AMF'))]
if pos == 'Strikers and Wingers':
    dfProspect = dfProspect[(dfProspect['Main Position'].str.contains('CF')) |
                           (dfProspect['Main Position'].str.contains('RW')) |
                           (dfProspect['Main Position'].str.contains('LW'))]
if pos == 'Forwards no ST (AM, W)':
    dfProspect = dfProspect[(dfProspect['Main Position'].str.contains('AMF')) |
                           (dfProspect['Main Position'].str.contains('RW')) |
                           (dfProspect['Main Position'].str.contains('LW')) |
#                                (dfProspect['Main Position'].str.contains('LAMF')) |
                           (dfProspect['Main Position'].str.contains('AMF'))]
if pos == 'Wingers':
    dfProspect = dfProspect[(dfProspect['Main Position'].str.contains('WF')) |
                           (dfProspect['Main Position'].str.contains('LAMF')) |
                           (dfProspect['Main Position'].str.contains('RAMF')) |
                           (dfProspect['Main Position'].str.contains('LW')) |
                           (dfProspect['Main Position'].str.contains('RW'))]
    dfProspect = dfProspect[~dfProspect['Main Position'].str.contains('WB')]
if pos == 'Midfielders (DM, CM, CAM)':
    dfProspect = dfProspect[(dfProspect['Main Position'].str.contains('CMF')) |
                           (dfProspect['Main Position'].str.contains('DMF')) |
                           (dfProspect['Main Position'].str.contains('AMF'))]
    dfProspect = dfProspect[~dfProspect['Main Position'].str.contains('LAMF')]
    dfProspect = dfProspect[~dfProspect['Main Position'].str.contains('RAMF')]
if pos == 'Central & Defensive Midfielders (DM, CM)':
    dfProspect = dfProspect[(dfProspect['Main Position'].str.contains('CMF')) |
                           (dfProspect['Main Position'].str.contains('DMF'))]
if pos == 'Central & Attacking Midfielders (CM, CAM)':
    dfProspect = dfProspect[(dfProspect['Main Position'].str.contains('CMF')) |
                           (dfProspect['Main Position'].str.contains('AMF'))]
    dfProspect = dfProspect[~dfProspect['Main Position'].str.contains('LAMF')]
    dfProspect = dfProspect[~dfProspect['Main Position'].str.contains('RAMF')]

if pos == 'Fullbacks (FBs/WBs)':
    dfProspect = dfProspect[(dfProspect['Main Position'].str.contains('LB')) |
                           (dfProspect['Main Position'].str.contains('RB')) |
                           (dfProspect['Main Position'].str.contains('WB'))]
if pos == 'Defenders (CB, FB/WB, DM)':
    dfProspect = dfProspect[(dfProspect['Main Position'].str.contains('LB')) |
                           (dfProspect['Main Position'].str.contains('RB')) |
                           (dfProspect['Main Position'].str.contains('WB')) |
                           (dfProspect['Main Position'].str.contains('CB')) |
                           (dfProspect['Main Position'].str.contains('LCB')) |
                           (dfProspect['Main Position'].str.contains('RCB')) |
                           (dfProspect['Main Position'].str.contains('DMF'))]
if pos == 'Centre-Backs':
    dfProspect = dfProspect[(dfProspect['Main Position'].str.contains('CB'))]

if pos == 'Strikers':
    dfProspect = dfProspect[(dfProspect['Main Position'].str.contains('CF'))]
if pos == 'Goalkeepers':
    dfProspect = dfProspect[(dfProspect['Main Position'].str.contains('GK'))]



fig = px.scatter(
    dfProspect,
    x = xx,
    y = yy,
    color = cc,
    color_continuous_scale = "RdYlGn_r",
    text = 'Player',
    hover_data=['Team', 'Age', 'Position', 'Minutes played'],
    hover_name = 'Player',
    title = '%s %s, %s & %s <br><sup>%s | Minimum %i minutes played | %s | Code by @BeGriffis</sup>' %(ssn,league,xx,yy,pos,mins,date),
    width=900,
    height=700)
fig.update_traces(textposition='top right', marker=dict(size=10, line=dict(width=1, color='black')))

fig.add_hline(y=dfProspect[yy].median(), name='Median', line_width=0.5)
fig.add_vline(x=dfProspect[xx].median(), name='Median', line_width=0.5)

st.plotly_chart(fig, theme=None, use_container_width=False)



with st.expander('Metric Glossary'):
    st.write('''
    Short & Medium Pass = Passes shorter than 40 meters.  \n
    Long Pass = Passes longer than 40 meters.  \n
    Smart Pass = A creative and penetrative pass that attempts to break the opposition's defensive lines to gain a significant advantage in attack.  \n
    Cross = Pass from the offensive flanks aimed towards a teammate in the area in front of the opponent’s goal.  \n
    Shot Assist = A pass where the receiver's next action is a shot.  \n
    Expected Assists (xA) = The expected goal (xG) value of shots assisted by a pass. xA only exists on passes that are Shot Assists.  \n
    xA per Shot Assist = The average xA of a player's shot assists.  \n
    Second Assist = The last action of a player from the goalscoring team, prior to an Assist by a teammate.  \n
    Third Assist = The penultimate action of a player from the goalscoring team, prior to an Assist by a teammate.  \n
    Expected Goals (xG) = The likelihood a shot becomes a goal, based on many factors (player position, body part of shot, location of assist, etc.).  \n
    Non-Penalty xG (npxG) = xG from non-penalty shots only.  \n
    npxG per Shot = The average npxG of a player's (non-penalty) shots.  \n
    Acceleration = A run with the ball with a significant speed up.  \n
    Progressive Carry = A continuous ball control by one player attempting to draw the team significantly closer to the opponent goal. (see Wyscout's glossary for more info)  \n
    Progressive Pass = A forward pass that attempts to advance a team significantly closer to the opponent’s goal.  \n
    Defensive Duel = When a player attempts to dispossess an opposition player to stop an attack progressing.  \n
    ''')
        

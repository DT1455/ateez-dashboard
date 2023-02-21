import pandas as pd

from dash import Dash, dcc, html, Input, Output
import dash_bootstrap_components as dbc
import dash_player as dp

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import matplotlib.pyplot as plt
from wordcloud import WordCloud

from datetime import datetime
from datetime import date

import nltk
from nltk.corpus import stopwords

url = 'https://github.com/DT1455/ateez-dashboard/blob/main/ateez.csv?raw=true'
df = pd.read_csv(url,
                 parse_dates=['publishedAt', 'date']).sort_values('publishedAt')

# Preparation for word cloud creation
words = ['oh', 'yeah', 'uh', 'blah', 'ta', 'da', 'ra', 'hey', 'oo', 'du', 'dum', 'ri', 'oeo', 'um', 'ay']
stop_words = set(stopwords.words('english'))
stop_words.update(words)

df['lyrics_no_stopwords'] = df['lyrics'].apply(lambda x: [item for item in str(x).split() if item not in stop_words])


app = Dash(external_stylesheets=[dbc.themes.CYBORG],
           meta_tags=[{'name': 'viewport',
                       'content': 'width=device-width, initial-scale=1.0'}])

# ATEEZ logo card
ateez = dbc.Card([
            dbc.CardImg(
                src="https://github.com/DT1455/ateez-dashboard/blob/main/ATEEZ.png?raw=true",
                className='bg-black',
                style={"opacity": 1,
                       "text-align": "center"},
            ),
], className='border-0',
   style={"width": "18rem"})

# Cards for overall likes, views, and comments stats
cardAll = dbc.CardGroup([
              dbc.Card(
                  dbc.CardBody([
                      html.H6('Likes',
                              className="card-title text-warning"),
                      html.P(id='lcardAll',
                             children=f"none",
                             className="card-text")
                  ])
              ),
              dbc.Card(
                  dbc.CardBody([
                      html.H6('Views',
                              className="card-title text-warning"),
                      html.P(id='vcardAll',
                             children=f"none",
                             className="card-text")
                  ])
              ),
              dbc.Card(
                  dbc.CardBody([
                      html.H6('Comments',
                              className="card-title text-warning"),
                      html.P(id='ccardAll',
                             children=f"none",
                             className="card-text")
                  ])
              ),
])

cardYear = dbc.CardGroup([
                dbc.Card(
                    dbc.CardBody([
                        html.H6('Likes',
                                className="card-title text-warning"),
                        html.P(id='lcardYear',
                               children=f"none",
                               className="card-text")
                    ])
                ),
                dbc.Card(
                    dbc.CardBody([
                        html.H6('Views',
                                className="card-title text-warning"),
                        html.P(id='vcardYear',
                               children=f"none",
                               className="card-text")
                    ])
                ),
                dbc.Card(
                    dbc.CardBody([
                        html.H6('Comments',
                                className="card-title text-warning"),
                        html.P(id='ccardYear',
                               children=f"none",
                               className="card-text")
                    ])
                ),
], className='mb-4')


# Cards for likes, views, and comments stats per year
cards1 = dbc.CardGroup([
             dbc.Card(
                 dbc.CardBody([
                     html.H6('Sentiment score',
                             className="card-title text-warning"),
                     html.P(id='sentiment',
                            children=f"none",
                            className="card-text",
                            style={'textAlign': 'center',
                                   'color': 'orange',
                                   'background-color': 'grey'}),
                 ])
             ),
             dbc.Card(
                 dbc.CardBody([
                     html.H6('Days from publication',
                             className="card-title text-warning"),
                     html.P(id='date',
                            children=f"none",
                            className="card-text",
                            style={'textAlign': 'center',
                                   'color': 'orange',
                                   'background-color': 'grey'})
                 ])
             )
], className='mb-4')


# Card for numeric input from user
card_num = dbc.Card(
               dbc.CardBody([
                   html.P("Choose a number of words in range of 1-100.",
                          style={'textAlign': 'center',
                                 'color': 'warning',
                                 'background-color': 'warning'}),
                   dbc.Input(id='word_number', value=25,
                             type='number', min=1,
                             max=100, step=1)
               ])
)


app.layout = dbc.Container([
                 dbc.Row([
                     dbc.Col(
                         dbc.Card(ateez, className='border-0'),
                         width="auto")
                 ], justify="center"),
                 dbc.Row([
                     dbc.Col([
                         dcc.Dropdown(id='song_name', multi=False,
                                      clearable=False, value=df['song'][0],
                                      options=[{'label': x, 'value': x}
                                               for x in df['song'].unique()],
                                      className='text-black'),
                         dp.DashPlayer(id="player", controls=True,
                                       width="100%", height="480px",
                                       url="https://www.youtube.com/embed/RqJ1rH9M5G0")
                     ]),
                     dbc.Col([
                         cards1,
                         html.H4("Rank in year of publication",
                                 className='text-center text-warning font-weight-bolder bg-black mb-4'),
                         cardYear,
                         html.H4("Overall rank",
                                 className='text-center text-warning font-weight-bolder bg-black mb-4'),
                         cardAll
                     ])
                 ]),
                 dbc.Row([
                     html.H4("Word cloud of song's lyrics",
                             className="card-title text-center text-warning bg-grey py-4"),
                     dbc.Col(
                         dbc.Card(card_num, color='black'), width="auto")
                 ], justify="center"),
                 dbc.Row([
                     dbc.Col(
                         dcc.Graph(id='wordcloud'))
                 ])
], fluid=True)


@app.callback(
    [Output('player', 'url'),
     Output('sentiment', 'children'),
     Output('sentiment', 'style'),
     Output('date', 'children'),
     Output('vcardAll', 'children'),
     Output('lcardAll', 'children'),
     Output('ccardAll', 'children'),
     Output('vcardYear', 'children'),
     Output('lcardYear', 'children'),
     Output('ccardYear', 'children'),
     Output('wordcloud', 'figure')],
    [Input('song_name', 'value'),
     Input('word_number', 'value')]
)
def layout(song, number):

    df_song = df[df['song'] == song]

    # Days from publication
    now = date.today()
    publ = df.loc[df['song'] == song, 'date'].item().date()
    day = (now - publ).days

    # Update player
    id_video = df.loc[df['song'] == song, 'video_id']
    video_src = "https://www.youtube.com/embed/" + id_video

    # Sentiment score
    score = df.loc[df['song'] == song, 'score'].item()

    if score > 0:
        bc = {'textAlign': 'center',
              'color': 'white',
              'background-color': 'grey'}
    if score < 0:
        bc = {'textAlign': 'center',
              'color': 'black',
              'background-color': 'grey'}

    # Update cards of overall stats
    viewsall = df_song['viewRankAll']
    likesall = df_song['likeRankAll']
    commentsall = df_song['commentRankAll']

    # Update cards of yearly stats
    view = df_song['viewRank']
    like = df_song['likeRank']
    comment = df_song['commentRank']

    # Word cloud
    all_words = list([a for b in df_song['lyrics_no_stopwords'].tolist() for a in b])
    all_words_str = ' '.join(all_words)

    wordcloud = WordCloud(width=2000, height=1000,
                          background_color='black',
                          max_words=number,
                          colormap='viridis',
                          collocations=False).generate(all_words_str)

    fig = px.imshow(wordcloud)
    fig.update_xaxes(showticklabels=False)
    fig.update_yaxes(showticklabels=False)
    fig.update_layout({'paper_bgcolor': 'black',
                       'plot_bgcolor': 'black'})

    return video_src, score, bc, day, viewsall, likesall, commentsall, view, like, comment, fig


if __name__ == '__main__':
    app.run_server(debug=True)

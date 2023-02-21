import pandas as pd

from dash import Dash, dcc, html, Input, Output
import dash_bootstrap_components as dbc

import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import matplotlib.pyplot as plt
from wordcloud import WordCloud

import nltk
nltk.download('stopwords')
from nltk.corpus import stopwords

url = 'https://github.com/DT1455/ateez-dashboard/blob/main/ateez.csv?raw=true'
df = pd.read_csv(url,
                 parse_dates=['publishedAt', 'date']).sort_values('publishedAt')

# Preparation for word cloud creation
words = ['oh', 'yeah', 'uh', 'blah', 'ta', 'da', 'ra', 'hey', 'oo', 'du', 'dum', 'ri', 'oeo', 'um', 'ay']
stop_words = set(stopwords.words('english'))
stop_words.update(words)

df['lyrics_no_stopwords'] = df['lyrics'].apply(lambda x: [item for item in str(x).split() if item not in stop_words])

# Bar plot
fig3 = px.bar(df, x='song', y='score', color_discrete_sequence=["orange"],
              labels={'score': 'Score', 'song': ''})
fig3.update_layout({'plot_bgcolor': 'black',
                    'paper_bgcolor': 'black',
                    'font_color': 'white'})

app = Dash(external_stylesheets=[dbc.themes.CYBORG],
           meta_tags=[{
                'name': 'viewport',
                'content': 'width=device-width, initial-scale=1.0'
           }])
server = app.server

# ATEEZ logo card
ateez = dbc.Card([
            dbc.CardImg(
                src="https://github.com/DT1455/ateez-dashboard/blob/main/ATEEZ.png?raw=true",
                className='bg-black',
                style={"opacity": 1,
                       "text-align": "center"}
            ),
], className='border-0',
   style={"width": "18rem"})

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
                         dbc.Card(ateez, className='border-0'), width="auto")
                 ], justify="center"),
                 dbc.Row([
                    dcc.Graph(id='graph-with-slider')
                 ]),
                 dbc.Row([
                    dcc.Slider(df['publishedAt'].dt.year.min(),
                               df['publishedAt'].dt.year.max(),
                               step=None,
                               value=df['publishedAt'].dt.year.min(),
                               marks={str(year): str(year) for year in df['publishedAt'].dt.year.unique()},
                               id='year-slider')
                 ]),
                 dbc.Row([
                    html.H4("Word cloud of lyrics per year",
                            className="card-title text-center text-warning bg-grey py-5"),
                    dbc.Col(
                        dbc.Card(card_num, color='black'), width="auto")
                 ], justify="center"),
                 dbc.Row([
                    dbc.Col(
                        dcc.Graph(id='wordcloud'))
                 ]),
                 dbc.Row([
                     html.H4("Sentiment score of songs",
                             className='text-center text-warning font-weight-bolder border-warning py-4'),
                     dcc.Graph(figure=fig3)
                 ])
], fluid=True)


@app.callback(
    [Output('graph-with-slider', 'figure'),
     Output('wordcloud', 'figure')],
    [Input('year-slider', 'value'),
     Input('word_number', 'value')]
)
def layout(selected_year, number):

    fin_df = df[df['publishedAt'].dt.year == selected_year]

    # Bar plots for likes, views, and comments
    fig = make_subplots(rows=1, cols=3,
                        subplot_titles=('Likes', 'Views', 'Comments'))
    fig.add_trace(go.Bar(x=fin_df['song'], y=fin_df['likeCount'],
                         marker_color='orange'), row=1, col=1)
    fig.add_trace(go.Bar(x=fin_df['song'], y=fin_df['viewCount'],
                         marker_color='darkorange'), row=1, col=2)
    fig.add_trace(go.Bar(x=fin_df['song'], y=fin_df['commentCount'],
                         marker_color='orangered'), row=1, col=3)
    fig.update_layout(showlegend=False)
    fig.update_layout({'paper_bgcolor': 'black',
                       'plot_bgcolor': 'black',
                       'font_color': 'white'})

    # Word cloud
    all_words = list([a for b in fin_df['lyrics_no_stopwords'].tolist() for a in b])
    all_words_str = ' '.join(all_words)

    wordcloud = WordCloud(width=2000, height=1000,
                          background_color='black',
                          max_words=number,
                          colormap='viridis',
                          collocations=False).generate(all_words_str)

    fig2 = px.imshow(wordcloud)
    fig2.update_xaxes(showticklabels=False)
    fig2.update_yaxes(showticklabels=False)
    fig2.update_layout({'paper_bgcolor': 'black',
                        'plot_bgcolor': 'black'})

    return fig, fig2


if __name__ == '__main__':
    app.run_server(debug=True)

import dash
from dash.dependencies import Output, Input, State
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import numpy as np


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets, update_title=None)
server = app.server

# ---------------- starting parameters ----------------
n = 25
speed = 120
start_data = np.random.choice([-1, 1], size=(n, n))
replace = 1  # true

fig = go.Figure()
fig.add_trace(
    go.Heatmap(z=np.random.choice([-1, 1], (n, n)),
               colorscale=[[0, "rgb(235, 103, 103)"],
                           [0.9, "rgb(103, 230, 114)"],
                           [1, "rgb(103, 230, 114)"]],
               colorbar=dict(tick0=-1, dtick=2),
               zmid=0
               )
            )


fig.update_layout(
                  showlegend=False, autosize=True,
                  title={'text': "q-voter model simulation",
                         'y': 0.95,
                         'x': 0.5,
                         'font': {'size': 40},
                         'xanchor': 'center',
                         'yanchor': 'top'},
                  )

fig2 = go.Figure()
fig2.add_trace(
    go.Scatter(x=[0], y=[np.sum(start_data)/(n*n)],
               line=dict(color="rgb(103, 230, 114)", width=2))
              )

fig2.update_layout(showlegend=True, autosize=True, title="Average opinion graph", xaxis_title="MCS")

app.layout = html.Div(id="page", children=[
        dcc.Store(id='value_T'),
        html.Div(
            id='left_col',
            children=[html.Div(id='graph_parent', children=[
                      dcc.Graph(figure=fig, id='live-graph', animate=True)]),
                      dcc.Interval(id='interval', interval=1 * 10**7, n_intervals=1),
                      html.Div(id='button_parent', children=[
                            html.Button("START / STOP", id='start_stop', n_clicks=0),
                            html.Button("SET", id='set', n_clicks=0)]),
                      dcc.Store(id='data', data=(start_data, 0, 0.1, 3, n, 'random', replace))
                      ]
                    ),
        html.Div(
            id='right_col',
            children=[html.Div(id='graph2_parent', children=[
                      dcc.Graph(figure=fig2, id='live-graph2')]),
                      html.Div(id="input_parent", children=[
                          html.Label("N = ", id='n_label', style={'font-size': '20px'}),
                          dcc.Input(
                              id="n", type="number", placeholder=25, value=25,
                              min=5, max=1000, step=1,
                          ),
                          dcc.RadioItems(
                            id='model',
                            options=[
                                {'label': 'conformity + independence', 'value': 'c_i'},
                                {'label': 'conformity + anticonformity', 'value': 'c_a'},
                                    ],
                            value='c_i',
                          ),
                          dcc.RadioItems(
                            id='draw',
                            options=[
                                {'label': '  drawing q neighb. with replacement⠀⠀', 'value': 1},
                                {'label': '  drawing q neighb. without replacement', 'value': 0},
                                    ],
                            value=1,
                          ),
                          dcc.RadioItems(
                            id='start_state',
                            options=[
                                {'label': 'random', 'value': 'random'},
                                {'label': 'circle', 'value': 'circle'},
                                {'label': 'checkboard', 'value': 'checkboard'},
                                {'label': 'solid', 'value': 'solid'}
                                    ],
                            value='random',
                            labelStyle={'display': 'inline-block', "margin-left": "5%"}
                          ),
                          html.Label("q = ", id='q_label', style={'font-size': '20px'}),
                          dcc.Input(
                              id="q", type="number", placeholder=3, value=3,
                              min=1, max=8, step=1,
                          ),
                          html.Label("p = ", id='p_label', style={'font-size': '20px'}),
                          dcc.Input(
                              id="p", type="number", placeholder=0.5, value=0.5,
                              min=0.01, max=1, step=0.01,
                          ),
                          html.Label("f = ", id='f_label', style={'font-size': '20px'}),
                          dcc.Input(
                              id="f", type="number", placeholder=0.5, value=0.5,
                              min=0.01, max=1, step=0.01,
                          ),
                          html.Label(" ", id='bottom_label', style={'font-size': '20px'}),
                        ])
                      ]
                    )
            ]
)


@app.callback(Output('live-graph', 'extendData'),
              Output('live-graph2', 'figure'),
              Output('data', 'data'),
              Input('interval', 'n_intervals'),
              Input('live-graph2', 'figure'),
              Input('set', 'n_clicks'),
              State('data', 'data'),
              State('n', 'value'),
              State('q', 'value'),
              State('p', 'value'),
              State('f', 'value'),
              State('start_state', 'value'),
              State('draw', 'value'))
def update_data(n_intervals,  figure, set_click, data, n, q, p, f, start_state, with_replace):
    ctx = dash.callback_context
    if ctx.triggered[0]['prop_id'].split('.')[0] == 'set':
        if start_state == 'random':
            state = np.random.choice([-1, 1], size=(n, n))
        elif start_state == 'circle':
            state = np.ones((n, n))
            a, b = int(n / 2), int(n / 2)
            r = int(n / 2.6)
            y, x = np.ogrid[-a:n - a, -b:n - b]
            mask = x * x + y * y <= r * r
            state[mask] = -1
        elif start_state == 'checkboard':
            state = np.indices((n, n)).sum(axis=0) % 2
            state[state == 0] = -1
        else:
            state = np.ones((n, n))

        new_data = state, p, f, q, n, start_state, with_replace
        y_new = np.sum((np.array(new_data[0])))/(n*n)
        t = go.Scatter(x=[1], y=[y_new], line=dict(color="rgb(103, 230, 114)", width=2))
        l = go.Layout(showlegend=False, autosize=True, title="Average opinion graph", xaxis_title={'text': "MCS"})

        return (dict(z=[new_data[0]]), [0], new_data[4]), {'data': [t], 'layout': l}, new_data

    # heatmap
    M, p, f, q, n, start_state, with_replace = data
    for agent in range(50):
        i, j = np.random.randint(0, n, size=2)
        nbs = [M[i % n][(j + 1) % n],
               M[i % n][(j - 1) % n],
               M[(i+1) % n][j % n],
               M[(i-1) % n][j % n],
               M[(i + 1) % n][(j + 1) % n],
               M[(i - 1) % n][(j - 1) % n],
               M[(i+1) % n][(j - 1) % n],
               M[(i-1) % n][(j + 1) % n]]
        if np.random.rand() <= p:
            if np.random.rand() < f:
                M[i][j] = -M[i][j]
        else:
            picked_nbs = np.random.choice(nbs, size=q, replace=with_replace)
            if np.all(picked_nbs == picked_nbs[0]):
                M[i][j] = picked_nbs[0]

    # scatter
    y_new = figure['data'][0]['y']
    y_new.append(np.sum((np.array(data[0])))/(n*n))
    t = go.Scatter(x=list(range(n_intervals + 1)), y=y_new, line=dict(color="rgb(103, 230, 114)", width=2))
    l = go.Layout(showlegend=False, autosize=True, title="Average opinion graph", xaxis_title={'text': "MCS"})

    return (dict(z=[M]), [0], n), {'data': [t], 'layout': l}, (M, p, f, q, n, start_state, with_replace)


@app.callback(Output('interval', 'interval'), Input('start_stop', 'n_clicks'))
def stop(clicks):
    if clicks % 2:
        return speed
    else:
        return 10**7


if __name__ == '__main__':
    app.run_server(debug=True)

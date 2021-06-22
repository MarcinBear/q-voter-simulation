import dash
from dash.dependencies import Output, Input, State
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import numpy as np


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets, update_title=None)
server = app.server

n = 25
speed = 50
start_data = np.random.choice([-1, 1], size=(n, n))

fig = go.Figure()
fig.add_trace(go.Heatmap(z=np.random.choice([-1, 1], (n, n)),
                         colorscale=[[0, "rgb(235, 103, 103)"],
                                     [0.9, "rgb(103, 230, 114)"],
                                     [1, "rgb(103, 230, 114)"]]))

fig.update_layout(
                  showlegend=False, autosize=False, width=800, height=800,
                  title={
                            'text': "q-voter model simulation",
                            'y': 0.95,
                            'x': 0.5,
                            'font': {'size': 40},
                            'xanchor': 'center',
                            'yanchor': 'top'},
                  )

fig2 = go.Figure()
fig2.add_trace(go.Scatter(x=[0], y=[np.sum((start_data == 1))], line=dict(color="rgb(103, 230, 114)", width=2)))
fig2.update_layout(
                  showlegend=False, autosize=False, width=900, height=400,
                  title={
                            'text': " ",
                            'y': 0.95,
                            'x': 0.5,
                            'font': {'size': 40},
                            'xanchor': 'center',
                            'yanchor': 'top'},
                  )

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
                      dcc.Store(id='data', data=(start_data, 0, 0.1, 3, n))
                      ]
                    ),
        html.Div(
            id='right_col',
            children=[html.Div(id='graph2_parent', children=[
                      dcc.Graph(figure=fig2, id='live-graph2')])
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
              State('data', 'data'))
def update_data(n_intervals,  figure, set_click, data):

    ctx = dash.callback_context
    if ctx.triggered[0]['prop_id'].split('.')[0] == 'set':
        n_stiff = 50
        p_stiff = 0.1
        f_stiff = 0.1
        nbs_stiff = 3
        new_data = np.random.choice([-1, 1], size=(n_stiff, n_stiff)), p_stiff, f_stiff, nbs_stiff, n_stiff

        y_new = np.sum((np.array(new_data[0]) == 1))
        t = go.Scatter(x=[1], y=[y_new], line=dict(color="rgb(103, 230, 114)", width=2))

        return (dict(z=[new_data[0]]), [0], new_data[4]), {'data': [t]}, new_data

    # heatmap
    M, p, f, num_of_nbs, n = data
    for agent in range(n):
        i, j = np.random.randint(1, n-1, size=2)
        nbs = [M[i][j + 1], M[i][j - 1], M[i+1][j], M[i-1][j]]
        if np.random.rand() <= p:
            if np.random.rand() < f:
                M[i][j] = -M[i][j]
        else:
            picked_nbs = np.random.choice(nbs, size=num_of_nbs)
            if np.all(picked_nbs == picked_nbs[0]):
                M[i][j] = picked_nbs[0]

    # scatter
    y_new = figure['data'][0]['y']
    y_new.append(np.sum((np.array(data[0]) == 1)))
    t = go.Scatter(x=list(range(n_intervals + 1)), y=y_new, line=dict(color="rgb(103, 230, 114)", width=2))

    return (dict(z=[M]), [0], n), {'data': [t]}, (M, p, f, num_of_nbs, n)


@app.callback(Output('interval', 'interval'), Input('start_stop', 'n_clicks'))
def stop(clicks):
    if clicks % 2:
        return speed
    else:
        return 10**7


if __name__ == '__main__':
    app.run_server(debug=True)

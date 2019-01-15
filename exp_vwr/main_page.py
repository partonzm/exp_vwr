from dash import Dash
from werkzeug.wsgi import DispatcherMiddleware
import flask
from werkzeug.serving import run_simple
import dash_html_components as html

server = flask.Flask(__name__)

dash_app1 = Dash(__name__, server = server, url_base_pathname='/app/arcbase6.py' )
dash_app2 = Dash(__name__, server = server, url_base_pathname='/apps/arcbase7.py')

dash_app1.layout = html.Div([html.H1('Hi there, I am app1 for dashboards')])
dash_app2.layout = html.Div([html.H1('Hi there, I am app2 for reports')])

@server.route('/')
@server.route('/hello')
def hello():
    return 'hello world!'

@server.route('/exp_viz')
def render_dashboard():
    return flask.redirect('/apps/arcbase6.py')


@server.route('/reports')
def render_reports():
    return flask.redirect('/apps/arcbase7.property')

app = DispatcherMiddleware(server, {
    '/apps/arcbase6.py': dash_app1.server,
    '/apps/arcbase7.py': dash_app2.server
})

run_simple('0.0.0.0', 8080, app, use_reloader=True, use_debugger=True)

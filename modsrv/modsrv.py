import rethinkdb as r
from flask import Flask
from environconfig import EnvironConfig
from environconfig import StringVar, IntVar

class DBCfg(EnvironConfig):
    """Database configuration from the environment."""
    HOSTNAME = StringVar(default='rethinkdb')
    PORT = IntVar(default=28015)

app = Flask(__name__)


@app.route('/')
def index():
    return '<h1>Hello World!</h1>'


@app.route('/user/<name>')
def user(name):
    return '<h1>Hello, %s!</h1>' % name


if __name__ == '__main__':
    r.connect(DBCfg.HOSTNAME, DBCfg.PORT).repl()
    r.db('test').table_create('tv_movies').run()
    r.table('tv_shows').insert({'name': 'Star Trek TNG'}).run()
    app.run(debug=True, port=8888)
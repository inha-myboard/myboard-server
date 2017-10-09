from flask import Flask, render_template, request
from flask.ext.mysql import MySQL
app = Flask(__name__)
mysql = MySQL()

@app.route('/')
def main():
	return(render_template("index.html"))

@app.route('/<name>')
def test(name = None):
	return(render_template(name))

if __name__ == "__main__":
	app.config.from_object('myboard.default_settings')
	app.config.from_envvar('MYBOARD_SETTINGS')

	mysql.init_app(app)
	mysql.connect()

	app.debug=True
	# app.debug=False
	app.run(host='127.0.0.1')
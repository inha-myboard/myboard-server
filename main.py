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
	#MySQL configurations
	app.config['MYSQL_DATABASE_USER'] = 'root'
	app.config['MYSQL_DATABASE_PASSWORD'] = '1234'
	app.config['MYSQL_DATABASE_DB'] = 'mydb'
	app.config['MYSQL_DATABASE_HOST'] = '127.0.0.1'
	mysql.init_app(app)
	mysql.connect()

	app.debug=True
	# app.debug=False
	app.run(host='127.0.0.1')
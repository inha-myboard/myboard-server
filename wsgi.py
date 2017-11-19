import myboard_server
from myboard_server import app
myboard_server.prepare()

if __name__ == "__main__":
	app.run(host='0.0.0.0')

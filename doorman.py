import flask
from twilio import twiml


OPEN_DOOR_WAV = 'https://dl.dropboxusercontent.com/u/191231/9.wav'

app = flask.Flask(__name__)


@app.route('/')
def open_door():
    response = twiml.Response()
    response.play(OPEN_DOOR_WAV)
    response.hangup()
    return unicode(response)

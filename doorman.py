import flask
import os
import redis
from flask import request
from twilio import twiml


OPEN_DOOR_WAV = 'https://dl.dropboxusercontent.com/u/191231/9.wav'

app = flask.Flask(__name__)
app.debug = True
redis_client = redis.Redis.from_url(os.environ['REDIS_URL'])
print redis_client
SECRET_KEY = u'1234'
DOOR_IS_OPEN = 'door-open'
TIMEOUT = 60  # seconds


@app.route('/knock', methods=['POST'])
def knock():
    body = request.form['Body']
    response = twiml.Response()
    if body == SECRET_KEY:
        redis_client.set(DOOR_IS_OPEN, 'true')
        redis_client.expire(DOOR_IS_OPEN, 60)
        response.sms(
            u'Passcode accepted. Please dial from the box in the next minute.'
        )
    else:
        response.sms(u'Passcode incorrect! Please try again.')

    return unicode(response)


@app.route('/open')
def open_door():
    response = twiml.Response()
    if redis_client.get(DOOR_IS_OPEN) == 'true':
        response.play(OPEN_DOOR_WAV)
    else:
        response.say(u'Sorry, the door is locked.', voice='alice')
    response.hangup()
    return unicode(response)


if __name__ == '__main__':
    app.debug = True
    app.run()

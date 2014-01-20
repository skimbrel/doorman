import flask
import os
import redis
from flask import request
from twilio import twiml


app = flask.Flask(__name__)
app.debug = True
redis_client = redis.Redis.from_url(os.environ['REDIS_URL'])

SECRET_KEY = os.environ['SECRET_KEY']
DOOR_IS_OPEN = 'door-open'
TIMEOUT = 60  # seconds
OPEN_SEQUENCE = 'ww999'


@app.route('/knock', methods=['POST'])
def knock():
    body = request.form['Body']
    response = twiml.Response()
    if body == SECRET_KEY:
        redis_client.set(DOOR_IS_OPEN, 'true')
        redis_client.expire(DOOR_IS_OPEN, 60)
        response.message(
            u'Passcode accepted. Please dial from the box in the next minute.'
        )
    else:
        response.message(u'Passcode incorrect! Please try again.')

    return unicode(response)


@app.route('/open')
def open_door():
    response = twiml.Response()
    if redis_client.get(DOOR_IS_OPEN) == 'true':
        response.play(digits=OPEN_SEQUENCE)

    else:
        with response.gather(action=u'/digits', finishOnKey=u'#') as g:
            g.say(u'Please enter the passcode, followed by the pound key.',
                  voice=u'alice')
            g.pause(length=5)

        response.say(
            u"Sorry, you didn't enter the passcode in time. Pleas try again.",
            voice=u'alice',
        )

    response.hangup()
    return unicode(response)


@app.route('/digits', methods=['POST'])
def gather_digits():
    response = twiml.Response()
    digits = request.form['Digits']
    if not digits:
        response.say(
            u"Sorry, you didn't enter the passcode in time. Please try again.",
            voice=u'alice',
        )

    elif digits == SECRET_KEY:
        response.say(u'Passcode accepted. Please enter.', voice=u'alice')
        response.play(OPEN_SEQUENCE)

    else:
        response.say(
            u"Sorry, that wasn't the right passcode. Please try again.",
            voice=u'alice',
        )

    response.hangup()
    return unicode(response)


if __name__ == '__main__':
    app.debug = True
    app.run()

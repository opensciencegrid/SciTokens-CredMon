
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash, session
from requests_oauthlib import OAuth2Session
import os
import urllib
import requests
import json

app = Flask(__name__)
app.secret_key = ':a\xfdq\x8b.\xc9\x96\xc1\x96K\xc3\xceJ\x12\x98\xa2\x81\xc4\xa50\xfa\x82\n'
client_id = "m293qpazhd04ka6uibyuwe3wvkx0y4hd"
client_secret = "Sage2NJDln497xNjsW37XGKJSDqwHnQn"
redirect_uri = "http://localhost/boxreturn"

credential_queue = None

@app.route('/')
def index():
     return render_template('index.html')

@app.route('/login')
def login():
     """
     Go to Box, and get some oauth stuff
     """
     oauth = OAuth2Session(client_id, redirect_uri=redirect_uri)
     authorization_url, state = oauth.authorization_url("https://account.box.com/api/oauth2/authorize")
     # State is used to prevent CSRF, keep this for later.
     session['oauth_state'] = state
     return redirect(authorization_url)


@app.route('/boxreturn')
def boxreturn():
     """
     Coming back from box
     """
     print(request.args)
     oauth = OAuth2Session(client_id, state=session['oauth_state'])
     token = oauth.fetch_token(
        'https://api.box.com/oauth2/token',
        authorization_response=request.url,
        # Google specific extra parameter used for client
        # authentication
        client_secret=client_secret)
     print token
     
     header = {'Authorization': 'Bearer %s' % token['access_token']}
     post_data = {'attributes': json.dumps({'name': 'testing.txt', 'parent': {'id': '0'}})}
     file_data = "This is the test file data!"
     returned_post = oauth.post("https://upload.box.com/api/2.0/files/content", data=post_data, files={'file': ('stuff.txt', file_data)})
     credential_queue.put(token)
     #requests.post("https://upload.box.com/api/2.0/files/content",  headers=header)
     print(returned_post.text)
     return render_template('success.html')


def start_webserver(queue):
     print "Starting webserver"
     global credential_queue
     credential_queue = queue
     os.environ['OAUTHLIB_INSECURE_TRANSPORT']="1"
     app.run(debug=True, use_reloader=False, port=80)

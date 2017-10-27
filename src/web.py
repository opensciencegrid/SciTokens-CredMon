
from flask import Flask, request, session, g, redirect, url_for, abort, \
    render_template, flash, session
from requests_oauthlib import OAuth2Session
import os
import urllib
import requests
import json
from urlparse import urlparse
from utils import ReadConfiguration, GetProviders, GetProviderOptions

app = Flask(__name__)
app.secret_key = ':a\xfdq\x8b.\xc9\x96\xc1\x96K\xc3\xceJ\x12\x98\xa2\x81\xc4\xa50\xfa\x82\n'
redirect_uri = "https://osgsubmit.unl.edu/boxreturn"

credential_queue = None

@app.route('/')
def index():
    
    # Get the username
    auth = request.authorization
    username = auth.username
    session['local_username'] = username
    
    return render_template('index.html')

@app.route('/login')
def login():
    """
    Go to Box, and get some oauth stuff
    """
    box_client_id = GetProviderOptions("Box.com", "client_id")
    oauth = OAuth2Session(box_client_id, redirect_uri=redirect_uri)
    authorization_url, state = oauth.authorization_url("https://account.box.com/api/oauth2/authorize")
    # State is used to prevent CSRF, keep this for later.
    session['oauth_state'] = state
    return redirect(authorization_url)


@app.route('/boxreturn')
def boxreturn():
    """
    Coming back from box
    """
    box_client_id = GetProviderOptions("Box.com", "client_id")
    oauth = OAuth2Session(box_client_id, state=session['oauth_state'])
    
    # Convert http url to https
    if not request.url.startswith("https"):
        updated_url = "https" + request.url[4:]
    else:
        updated_url = request.url
    
    box_client_secret = GetProviderOptions("Box.com", "client_secret")
    token = oauth.fetch_token(
       'https://api.box.com/oauth2/token',
       authorization_response=updated_url,
       # Google specific extra parameter used for client
       # authentication
       client_secret=box_client_secret)
    print token
    session['box_token'] = json.dumps(token)
    
    # Get the user info
    returned_get = oauth.get("https://api.box.com/2.0/users/me")
    box_user = returned_get.json()
    session['box_username'] = box_user['login']
    
    credential_queue.put(token)
    session['box'] = True
    return redirect("/")

@app.route('/test_box')
def test_box():
    """
    Test the Box connection
    
    Returns a json object:
    status:         1 - indicates success
                    0 - indicates failure
    statusMessage:  string of either the success or failure
    
    """
    # Load the token
    token = json.loads(session['box_token'])
    box_client_id = GetProviderOptions("Box.com", "client_id")
    oauth = OAuth2Session(box_client_id, token=token)
    toReturn = { 'status': 0, 'statusMessage': 'unknown' }
    
    # Look for htcondor folder
    returned_get = oauth.get("https://api.box.com/2.0/folders/0/items")
    found_condor_folder = False
    condor_folder_info = None
    print returned_get.json()
    for folder in returned_get.json()['entries']:
        if folder['type'] == "folder" and folder['name'] == "htcondor":
            found_condor_folder = True
            condor_folder_info = folder
    
    if not found_condor_folder:
        folder_info = json.dumps({"name": "htcondor", "parent": {"id": "0"}})
        condor_folder_info = oauth.post("https://api.box.com/2.0/folders", data=folder_info).json()
        print condor_folder_info
    
    # Put a test file inside the htcondor directory
    post_data = {'attributes': json.dumps({'name': 'testing.txt', 'parent': {'id': str(condor_folder_info['id'])}})}
    file_data = "This is the test file data created from the host: %s" % request.url
    returned_post = oauth.post("https://upload.box.com/api/2.0/files/content", data=post_data, files={'file': ('testing.txt', file_data)})
    print returned_post
    if returned_post.status_code != 201:
        toReturn['status'] = 0
        returned_data = returned_post.json()
        print returned_data
        if "message" in returned_data:
            print "Printing message"
            toReturn['statusMessage'] = "Failed to create testing file \"testing.txt\" in htcondor directory: %s" % returned_data['message']
        #return json.dumps(toReturn)
    
    toReturn['status'] = 1
    toReturn['statusMessage'] = "Successfully created the test file in the htcondor directory"
    
    # Try to get a shared link of the directory
    public_link_options = json.dumps({'shared_link': {'access': 'open', 'password': None}})
    returned_put = oauth.put("https://api.box.com/2.0/folders/%s?fields=shared_link" % str(condor_folder_info['id']), data=public_link_options)
    print returned_put.json()
    if returned_put.status_code >= 200 and returned_put.status_code < 300:
        print "Within shared link area"
        returned_data = returned_put.json()
        print returned_data
        toReturn['sharedLink'] = returned_data['shared_link']['url']
    
    # Return a json object
    return json.dumps(toReturn)


def start_webserver(queue):
    print "Starting webserver"
    global credential_queue
    credential_queue = queue
    
    # Read in the configuration file
    ReadConfiguration(os.environ.get("CREDMON_WEB_CONFIG"))
    
    print "Providers: "
    print GetProviders()
    
    

    #os.environ['OAUTHLIB_INSECURE_TRANSPORT']="1"
    app.run(debug=True, use_reloader=False, port=8080)

import json
from flask import Flask, redirect, url_for, session
from authlib.integrations.flask_client import OAuth

app = Flask(__name__)
app.secret_key = '123'  # Change this to a random secret key

# Load client secrets from the JSON file
with open('client_secret.json', 'r') as file:
    client_secrets = json.load(file)

oauth = OAuth(app)

# Register the OAuth client using the loaded client secrets
google = oauth.register(
    name='google',
    client_id=client_secrets['web']['client_id'],
    client_secret=client_secrets['web']['client_secret'],
    access_token_url=client_secrets['web']['token_uri'],
    access_token_params=None,
    authorize_url=client_secrets['web']['auth_uri'],
    authorize_params=None,
    api_base_url='https://www.googleapis.com/oauth2/v1/',
    client_kwargs={'scope': 'openid email profile'},
    # Specify the correct redirect URI based on your application configuration
    redirect_uri=client_secrets['web']['redirect_uris'][0],
    jwks_uri= "https://www.googleapis.com/oauth2/v3/certs",
)

@app.route('/')
def index():
    email = dict(session).get('email', None)
    return f'Hello, {email}!' if email else 'Hello, please <a href="/login">login</a>'

@app.route('/login')
def login():
    redirect_uri = url_for('authorize', _external=True)
    return google.authorize_redirect(redirect_uri)

@app.route('/oauth2callback')
def authorize():
    token = google.authorize_access_token()
    resp = google.get('userinfo')
    user_info = resp.json()
    session['email'] = user_info['email']
    return redirect('/')


if __name__ == "__main__":
    app.run(debug=True)

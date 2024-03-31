import json
from flask import Flask, redirect, url_for, session,request,render_template,jsonify
from authlib.integrations.flask_client import OAuth
from db import Db

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
def index_page():
    return render_template('index.html')
@app.route('/main')
def main_page():
    return render_template('main.html')

@app.route('/login')
def login_page():
    return render_template('login.html')
@app.route('/signup')
def signup_page():
    return render_template('signup.html')
@app.route('/disconnect')
def disconnect():
    session.pop('email', None)
    return redirect('/')

@app.route('/login_google')
def login_with_google():
    redirect_uri = url_for('authorize', _external=True)
    return google.authorize_redirect(redirect_uri)

@app.route('/oauth2callback')
def authorize():
    token = google.authorize_access_token()
    resp = google.get('userinfo')
    user_info = resp.json()
    session['email'] = user_info['email']
    user = (user_info['email'],'none','google',user_info['given_name'],user_info['family_name'])
    with Db() as db:
         db.insert_user(user)

    return redirect('/main')

@app.route('/signup_email', methods=['POST'])
def signup():
    data = request.get_json()  # Get data as JSON
    user = (data['email'] , data['password'], 'email',data['first_name'],data['last_name'])
    try:
        with Db() as db:
             val = db.insert_user(user)
    except Exception as e:
        return jsonify({'status': 'error', 'message': 'signup failed - database problem'}), 401
    else:
        if val:
            return jsonify({'status': 'success', 'message': 'signup successful'})
        else:
            return jsonify({'status': 'error', 'message': 'there is already user with this email'})

@app.route('/login_email', methods=['POST'])
def login_via_email():
    data = request.get_json()  # Get data as JSON
    user = (data['email'], data['password'])
    with Db() as db:
        val = db.login(user)
    if val:
        session['email'] = user[0]
        print('cool cool cool')
        return jsonify({'status': 'success', 'message': 'Login successful'})
    else:
        return jsonify({'status': 'error', 'message': 'Login failed'}), 401


if __name__ == "__main__":
    app.run(debug=True)

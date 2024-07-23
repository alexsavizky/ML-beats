import json
import os
from flask import Flask, redirect, url_for, session, request, jsonify
from werkzeug.utils import secure_filename
from authlib.integrations.flask_client import OAuth
from db import Db

app = Flask(__name__)
app.secret_key = '123'  # Change this to a random secret key

# Load client secrets from the JSON file
with open('client_secret.json', 'r') as file:
    client_secrets = json.load(file)

oauth = OAuth(app)

# Register the OAuth client using the loaded client secretsa
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

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'mp3'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def index():
    email = session.get('email', None)
    if email:
        return f'Hello, {email}! <a href="/disconnect">Disconnect</a>'
    else:
        return 'Hello, please <a href="/login_google">login</a>'

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

    return redirect('/')

@app.route('/signup', methods=['POST'])
def signup():
    user = (request.form['email'] , request.form['password'], 'email',request.form['first_name'],request.form['last_name'])
    with Db() as db:
         db.insert_user(user)

@app.route('/login', methods=['POST'])
def login_via_email():
    user = (request.form['email'], request.form['password'])
    with Db() as db:
        val = db.login(user)
    if val:
        session['email'] = user[0]
        print('ccol cool cool')

@app.route('/upload', methods=['POST'])
def upload_file():
    # Check if the post request has the file part
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    # If the user does not select a file, the browser submits an empty file without a filename
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return jsonify({'message': 'File uploaded successfully', 'filename': filename}), 200
    return jsonify({'error': 'File type not allowed'}), 400

if __name__ == "__main__":
    # Create the upload folder if it doesn't exist
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.run(debug=True)
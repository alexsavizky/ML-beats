import firebase_admin
from firebase_admin import credentials

cred = credentials.Certificate({
    'apiKey': "AIzaSyC6TZDpVQccVkPgL91I7JQcWgZeNq73NB0",
    'authDomain': "ml-beats.firebaseapp.com",
    'projectId': "ml-beats",
    'storageBucket': "ml-beats.appspot.com",
    'messagingSenderId': "185662295334",
    'appId': "1:185662295334:web:1f2d846060562c9b2bc5e7",
    'measurementId': "G-BQMJBSRTJR"
})

firebase_admin.initialize_app(cred)
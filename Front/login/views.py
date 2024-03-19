from django.shortcuts import render
from django.contrib.auth import authenticate, login

def login_view(request):
    # Your logic for handling login here
    return render(request, 'login.html')
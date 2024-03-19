from django.shortcuts import render

def login_view(request):
    # Your view logic here
    return render(request, 'login.html')

from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.http import HttpResponse

def home(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'accounts/home.html')

def reset_admin_password(request):
    user = User.objects.get(username='YOUR_USERNAME')  # change this
    user.set_password('newpassword123')  # set new password
    user.save()
    return HttpResponse("Password reset successful")

def create_superuser(request):
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser(
            username='admin',
            email='admin@gmail.com',
            password='admin123'
        )
        return HttpResponse("Superuser created")
    else:
        return HttpResponse("Superuser already exists")
    
def register_view(request):

    if request.method == "POST":

        first_name = request.POST.get('first_name', '')
        last_name = request.POST.get('last_name', '')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')

        if password == password2:

            if User.objects.filter(email=email).exists():
                messages.error(request, "Email already exists")
                return redirect('register')

            user = User.objects.create_user(
                username=email,
                email=email,
                password=password
            )

            user.first_name = first_name
            user.last_name = last_name
            user.save()

            messages.success(request, "Account created successfully")
            return redirect('login')

        else:
            messages.error(request, "Passwords do not match")

    return render(request, 'accounts/register.html')


def login_view(request):

    if request.method == "POST":

        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, "Invalid email or password")

    return render(request, 'accounts/login.html')


@login_required
def logout_view(request):
    logout(request)
    return redirect('login')

def forgot_password(request):
    return render(request,'accounts/forgot-password.html')


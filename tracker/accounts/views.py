from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.http import HttpResponse


# ================= HOME =================
def home(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'accounts/home.html')


# ================= REGISTER =================
def register_view(request):
    if request.method == "POST":

        first_name = request.POST.get('first_name', '')
        last_name = request.POST.get('last_name', '')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')

        if password != password2:
            messages.error(request, "Passwords do not match")
            return redirect('register')

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists")
            return redirect('register')

        user = User.objects.create_user(
            username=email,   # email as username
            email=email,
            password=password
        )

        user.first_name = first_name
        user.last_name = last_name
        user.save()

        messages.success(request, "Account created successfully")
        return redirect('login')

    return render(request, 'accounts/register.html')


# ================= LOGIN (🔥 MAIN PART) =================
def login_view(request):

    # auto redirect if already logged in
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == "POST":
        identifier = request.POST.get("identifier")  # email or adm no
        password = request.POST.get("password")

        # 🔥 Detect if email or admission number
        if "@" in identifier:
            try:
                user_obj = User.objects.get(email=identifier)
                username = user_obj.username
            except User.DoesNotExist:
                username = None
        else:
            username = identifier  # admission number

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            role = user.profile.role

            if role == 'student':
                return redirect('student_dashboard')

            elif role == 'teacher':
                return redirect('teacher_dashboard')

            else:
                return redirect('dashboard')

        else:
            messages.error(request, "Invalid email/admission number or password")

    return render(request, "accounts/login.html")  # ✅ FIXED PATH


# ================= LOGOUT =================
@login_required
def logout_view(request):
    logout(request)
    return redirect('login')


# ================= FORGOT PASSWORD =================
def forgot_password(request):
    return render(request, 'accounts/forgot-password.html')


# ================= DEV HELPERS (REMOVE IN PROD) =================
def reset_admin_password(request):
    user = User.objects.get(username='admin')  # change if needed
    user.set_password('admin123')
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
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.db import IntegrityError, transaction
from django.contrib.auth.hashers import make_password
from django.core.exceptions import ValidationError
from django.shortcuts import redirect, render

from .models import UserProfile

def index(request):
    if request.method == "POST":
        return handle_login(request)
    return render(request, "index.html")


def handle_login(request):
    username = request.POST.get("username", "").strip()
    password = request.POST.get("password", "")
    user = authenticate(request, username=username, password=password)

    if user is None:
        return render(request, "index.html", {
            "login_error": "Invalid username or password.",
        }, status=401)

    login(request, user)
    return redirect("hero")


def signup_details(request):
    if request.method != "POST":
        return redirect("index")

    role = request.POST.get("role", "").strip()
    first_name = request.POST.get("first_name", "").strip()
    last_name = request.POST.get("last_name", "").strip()
    institutional_id = request.POST.get("idnumber", "").strip()
    graduation_term = request.POST.get("graduation", "").strip()
    password = request.POST.get("password", "")
    password_confirmation = request.POST.get("password_confirmation", "")

    errors = []
    if role not in dict(UserProfile.ROLE_CHOICES):
        errors.append("Choose a valid account type.")
    if not first_name or not last_name or not institutional_id:
        errors.append("Complete all required account details.")
    if role == UserProfile.ROLE_STUDENT and not graduation_term:
        errors.append("Students must provide an expected graduation term.")
    if password != password_confirmation:
        errors.append("Passwords do not match.")
    else:
        try:
            validate_password(password)
        except ValidationError as error:
            errors.extend(error.messages)
    if UserProfile.objects.filter(institutional_id=institutional_id).exists():
        errors.append("That institutional ID is already registered.")

    if errors:
        return render(request, "index.html", {
            "signup_errors": errors,
            "initial_view": "signup",
        }, status=400)

    request.session["signup_details"] = {
        "role": role,
        "first_name": first_name,
        "last_name": last_name,
        "institutional_id": institutional_id,
        "graduation_term": graduation_term,
        "password_hash": make_password(password),
    }
    return render(request, "index.html", {"initial_view": "upload"})


def signup_complete(request):
    if request.method != "POST":
        return redirect("index")

    details = request.session.get("signup_details")
    front = request.FILES.get("id_front")
    back = request.FILES.get("id_back")
    if not details or not front or not back or not request.POST.get("affirmation"):
        return render(request, "index.html", {
            "signup_errors": ["Provide both ID images and accept the verification statement."],
            "initial_view": "upload",
        }, status=400)

    username = details["institutional_id"]
    if User.objects.filter(username=username).exists():
        request.session.pop("signup_details", None)
        return render(request, "index.html", {
            "login_error": "An account already exists for that institutional ID.",
        }, status=400)

    try:
        with transaction.atomic():
            user = User.objects.create(
                username=username,
                first_name=details["first_name"],
                last_name=details["last_name"],
                password=details["password_hash"],
            )
            UserProfile.objects.create(
                user=user,
                role=details["role"],
                institutional_id=details["institutional_id"],
                graduation_term=details["graduation_term"],
                id_front=front,
                id_back=back,
            )
    except IntegrityError:
        return render(request, "index.html", {
            "signup_errors": ["That institutional ID is already registered."],
            "initial_view": "signup",
        }, status=400)

    request.session.pop("signup_details", None)
    login(request, user)
    messages.success(request, "Your PasaBuy account has been created.")
    return redirect("hero")


def hero_page(request):
    return render(request, "heropage.html")


def browser(request):
    return render(request, "browser.html")


def my_orders(request):
    return render(request, "myorders.html")


def upload_id(request):
    return render(request, "index.html", {"initial_view": "upload"})


def logout_view(request):
    logout(request)
    return redirect("index")
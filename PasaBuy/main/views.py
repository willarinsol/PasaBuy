import json
from datetime import datetime
from decimal import Decimal, InvalidOperation

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.db import IntegrityError, transaction
from django.db.models import Q
from django.contrib.auth.hashers import make_password
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.utils import timezone

from .models import FoodOrder, FoodOrderItem, FoodOrderReview, UserProfile

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


def expire_due_orders():
    now = timezone.now()
    local_time = timezone.localtime(now).time()
    FoodOrder.objects.filter(status=FoodOrder.STATUS_POSTED).filter(
        Q(due_at__lte=now)
        | Q(due_at__isnull=True, due_time__lte=local_time)
    ).update(status=FoodOrder.STATUS_CANCELLED)


def browser(request):
    expire_due_orders()
    orders = FoodOrder.objects.filter(
        status=FoodOrder.STATUS_POSTED,
    ).prefetch_related("items").order_by("-posted_at")
    if request.user.is_authenticated:
        orders = orders.exclude(poster=request.user)
    orders = list(orders)
    for order in orders:
        order.item_summary = ", ".join(
            f"{item.quantity}x {item.name}" for item in order.items.all()
        )
    return render(request, "browser.html", {"orders": orders})


def user_is_approved(user):
    return user.is_authenticated and getattr(
        getattr(user, "userprofile", None), "is_approved", False
    )


def my_orders(request):
    if not request.user.is_authenticated:
        return redirect("index")

    expire_due_orders()
    orders = FoodOrder.objects.filter(
        Q(poster=request.user) | Q(claimed_by=request.user)
    ).prefetch_related("items").select_related("poster", "claimed_by").order_by("-posted_at")
    orders = list(orders)
    for order in orders:
        order.item_summary = ", ".join(
            f"{item.quantity}x {item.name}" for item in order.items.all()
        )
        order.is_owner = order.poster_id == request.user.id
        order.is_runner = order.claimed_by_id == request.user.id

    return render(request, "myorders.html", {
        "orders": orders,
        "active_count": sum(order.status in {FoodOrder.STATUS_POSTED, FoodOrder.STATUS_CLAIMED} for order in orders),
        "ongoing_count": sum(order.status == FoodOrder.STATUS_CLAIMED and order.is_runner for order in orders),
        "completed_count": sum(order.status == FoodOrder.STATUS_COMPLETED for order in orders),
        "cancelled_count": sum(order.status == FoodOrder.STATUS_CANCELLED for order in orders),
    })


def order_payload(order, user):
    is_owner = user.is_authenticated and order.poster_id == user.id
    return {
        "id": order.id,
        "posterName": order.poster_name,
        "posterSid": order.student_id,
        "target": order.target_store,
        "deliver": order.delivery_location,
        "items": [
            {"name": item.name, "qty": item.quantity}
            for item in order.items.all()
        ],
        "desc": order.description,
        "tip": str(order.tip),
        "due": order.due_time.strftime("%I:%M %p").lstrip("0"),
        "posted": order.posted_at.strftime("%I:%M %p").lstrip("0"),
        "status": order.status,
        "canCancel": is_owner and order.status == FoodOrder.STATUS_POSTED,
        "cancelUrl": f"/order/{order.id}/cancel/",
        "canEdit": is_owner and order.status == FoodOrder.STATUS_POSTED,
        "editUrl": f"/order/{order.id}/description/",
        "canAccept": (
            user.is_authenticated
            and not is_owner
            and order.status == FoodOrder.STATUS_POSTED
        ),
        "acceptUrl": f"/order/{order.id}/accept/",
    }


def order_detail(request, order_id):
    expire_due_orders()
    try:
        order = FoodOrder.objects.prefetch_related("items").get(id=order_id)
    except FoodOrder.DoesNotExist:
        return redirect("browser")

    return render(request, "orderpage.html", {
        "initial_order": order_payload(order, request.user),
        "poster_name": "",
        "student_id": "",
    })


def order_page(request):
    profile = getattr(request.user, "userprofile", None)
    account_name = request.user.get_full_name() if request.user.is_authenticated else ""
    account_id = profile.institutional_id if profile else ""

    if request.method == "POST":
        if not request.user.is_authenticated:
            return JsonResponse({"error": "Log in before posting a PasaBuy."}, status=401)
        if not user_is_approved(request.user):
            return JsonResponse({
                "error": "Your account is awaiting manual KYC approval.",
            }, status=403)

        try:
            payload = json.loads(request.body)
            due_time = datetime.strptime(payload.get("dueInput", ""), "%H:%M").time()
            tip = Decimal(str(payload.get("tip", 0)))
        except (json.JSONDecodeError, TypeError, ValueError, InvalidOperation):
            return JsonResponse({"error": "Enter a valid due time and tip amount."}, status=400)

        poster_name = str(payload.get("posterName", "")).strip() or account_name.strip()
        student_id = str(payload.get("posterSid", "")).strip() or account_id
        target_store = str(payload.get("target", "")).strip()
        delivery_location = str(payload.get("deliver", "")).strip()
        description = str(payload.get("desc", "")).strip()
        raw_items = payload.get("items", [])

        if not poster_name or not student_id:
            return JsonResponse({"error": "Your name and student ID are required."}, status=400)
        if not target_store or not delivery_location or not isinstance(raw_items, list) or not raw_items:
            return JsonResponse({"error": "Complete the store, delivery location, and order items."}, status=400)
        if tip < 0:
            return JsonResponse({"error": "The tip cannot be negative."}, status=400)

        try:
            with transaction.atomic():
                order = FoodOrder.objects.create(
                    poster=request.user,
                    poster_name=poster_name,
                    student_id=student_id,
                    target_store=target_store,
                    delivery_location=delivery_location,
                    due_time=due_time,
                    due_at=timezone.make_aware(
                        datetime.combine(timezone.localdate(), due_time)
                    ),
                    description=description,
                    tip=tip,
                )
                for item in raw_items:
                    item_name = str(item.get("name", "")).strip()
                    quantity = int(item.get("qty", 1))
                    if not item_name or quantity < 1:
                        raise ValueError
                    FoodOrderItem.objects.create(
                        order=order,
                        name=item_name,
                        quantity=quantity,
                    )
        except (TypeError, ValueError):
            return JsonResponse({"error": "Each order item needs a name and valid quantity."}, status=400)

        return JsonResponse(order_payload(order, request.user), status=201)

    return render(request, "orderpage.html", {
        "poster_name": account_name,
        "student_id": account_id,
    })


def cancel_order(request, order_id):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Log in before cancelling an order."}, status=401)
    if request.method != "POST":
        return JsonResponse({"error": "Only POST requests can cancel an order."}, status=405)

    try:
        order = FoodOrder.objects.get(
            id=order_id,
            poster=request.user,
            status=FoodOrder.STATUS_POSTED,
        )
    except FoodOrder.DoesNotExist:
        return JsonResponse({"error": "You can only cancel your own active orders."}, status=404)

    order.status = FoodOrder.STATUS_CANCELLED
    order.save(update_fields=["status"])
    return JsonResponse({"status": order.status})


def update_order_description(request, order_id):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Log in before editing an order."}, status=401)
    if request.method != "POST":
        return JsonResponse({"error": "Only POST requests can edit an order."}, status=405)

    try:
        order = FoodOrder.objects.get(
            id=order_id,
            poster=request.user,
            status=FoodOrder.STATUS_POSTED,
        )
        payload = json.loads(request.body)
        description = str(payload.get("description", "")).strip()[:1000]
    except FoodOrder.DoesNotExist:
        return JsonResponse({"error": "Only the order owner can edit this order."}, status=404)
    except (json.JSONDecodeError, TypeError):
        return JsonResponse({"error": "Enter a valid description."}, status=400)

    order.description = description
    order.save(update_fields=["description"])
    return JsonResponse({"description": order.description})


def accept_order(request, order_id):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Log in before accepting an order."}, status=401)
    if request.method != "POST":
        return JsonResponse({"error": "Only POST requests can accept an order."}, status=405)
    if not user_is_approved(request.user):
        return JsonResponse({
            "error": "Your account is awaiting manual KYC approval.",
        }, status=403)

    expire_due_orders()
    try:
        order = FoodOrder.objects.get(
            id=order_id,
            status=FoodOrder.STATUS_POSTED,
        )
    except FoodOrder.DoesNotExist:
        return JsonResponse({"error": "This order is no longer available."}, status=404)
    if order.poster_id == request.user.id:
        return JsonResponse({"error": "You cannot accept your own order."}, status=403)

    order.status = FoodOrder.STATUS_CLAIMED
    order.claimed_by = request.user
    order.claimed_at = timezone.now()
    order.save(update_fields=["status", "claimed_by", "claimed_at"])
    return JsonResponse({"status": order.status})


def complete_order(request, order_id):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Log in before completing an order."}, status=401)
    if request.method != "POST":
        return JsonResponse({"error": "Only POST requests can complete an order."}, status=405)

    order = FoodOrder.objects.filter(
        id=order_id,
        status=FoodOrder.STATUS_CLAIMED,
        poster=request.user,
    ).select_related("claimed_by").first()
    if order is None:
        return JsonResponse({"error": "Only the order owner can complete this order."}, status=404)

    if order.claimed_by is None:
        return JsonResponse({"error": "This order has no assigned runner."}, status=400)

    try:
        payload = json.loads(request.body)
        rating = int(payload.get("rating"))
        review = str(payload.get("review", "")).strip()[:1000]
    except (json.JSONDecodeError, TypeError, ValueError):
        return JsonResponse({"error": "Choose a rating from 1 to 5."}, status=400)
    if rating < 1 or rating > 5:
        return JsonResponse({"error": "Choose a rating from 1 to 5."}, status=400)

    with transaction.atomic():
        FoodOrderReview.objects.create(
            order=order,
            reviewer=request.user,
            runner=order.claimed_by,
            rating=rating,
            review=review,
        )
        order.status = FoodOrder.STATUS_COMPLETED
        order.completed_at = timezone.now()
        order.save(update_fields=["status", "completed_at"])
    return JsonResponse({"status": order.status})


def user_page(request):
    return render(request, "userpage.html")


def info_page(request):
    return render(request, "info.html")


def upload_id(request):
    return render(request, "index.html", {"initial_view": "upload"})


def logout_view(request):
    logout(request)
    return redirect("index")
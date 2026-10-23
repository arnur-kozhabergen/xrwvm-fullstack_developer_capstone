import json
from functools import wraps
from datetime import date
import requests
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.db import IntegrityError
from django.views.decorators.http import require_GET, require_POST
from django.views.decorators.csrf import ensure_csrf_cookie
from .models import CarMake, CarModel
from . import restapis


def guarded(view):
    @wraps(view)
    def wrapped(request, *args, **kwargs):
        try:
            return view(request, *args, **kwargs)
        except (
            json.JSONDecodeError,
            UnicodeDecodeError,
            KeyError,
            TypeError,
            ValueError,
        ):
            return JsonResponse({"error": "Invalid request data."}, status=400)
        except requests.RequestException:
            return JsonResponse(
                {"error": "A dependent service is unavailable."}, status=502
            )

    return wrapped


def object_body(request, required_strings):
    data = json.loads(request.body)
    if not isinstance(data, dict):
        raise ValueError("An object is required")
    for key, maximum in required_strings.items():
        value = data.get(key)
        if not isinstance(value, str) or not value.strip() or len(value) > maximum:
            raise ValueError("Invalid string field")
    return data


@require_GET
@ensure_csrf_cookie
def session(request):
    return JsonResponse(
        {
            "userName": request.user.username if request.user.is_authenticated else "",
            "firstName": (
                request.user.first_name if request.user.is_authenticated else ""
            ),
            "lastName": request.user.last_name if request.user.is_authenticated else "",
        }
    )


@require_POST
@guarded
def login_user(request):
    data = object_body(request, {"userName": 150, "password": 1024})
    user = authenticate(request, username=data["userName"], password=data["password"])
    if user is None:
        return JsonResponse({"error": "Invalid username or password."}, status=401)
    login(request, user)
    return JsonResponse({"userName": user.username, "status": "Authenticated"})


@require_GET
def logout_request(request):
    # Retained GET solely for the course's explicit logout cURL contract.
    logout(request)
    return JsonResponse({"userName": ""})


@require_POST
@guarded
def registration(request):
    data = object_body(
        request,
        {
            "userName": 150,
            "password": 1024,
            "email": 254,
            "firstName": 150,
            "lastName": 150,
        },
    )
    username = data["userName"].strip()
    if not username or len(username) > 150:
        return JsonResponse(
            {"error": "Username is required, maximum 150 characters."}, status=400
        )
    user = User(
        username=username,
        email=data["email"],
        first_name=data["firstName"],
        last_name=data["lastName"],
    )
    try:
        validate_email(user.email)
        validate_password(data["password"], user)
        user.set_password(data["password"])
        user.save()
    except ValidationError as exc:
        return JsonResponse({"error": " ".join(exc.messages)}, status=400)
    except IntegrityError:
        return JsonResponse({"error": "Already Registered"}, status=409)
    login(request, user)
    return JsonResponse(
        {"userName": user.username, "status": "Authenticated"}, status=201
    )


@require_GET
@guarded
def get_dealerships(request, state="All"):
    endpoint = (
        "fetchDealers"
        if state == "All"
        else "fetchDealers/" + requests.utils.quote(state, safe="")
    )
    return JsonResponse({"status": 200, "dealers": restapis.get_request(endpoint)})


@require_GET
@guarded
def get_dealer_details(request, dealer_id):
    dealer = restapis.get_request(f"fetchDealer/{dealer_id}")
    return JsonResponse(
        {"status": 200 if dealer else 404, "dealer": dealer},
        status=200 if dealer else 404,
    )


@require_GET
@guarded
def get_dealer_reviews(request, dealer_id):
    reviews = restapis.get_request(f"fetchReviews/dealer/{dealer_id}")
    for review in reviews:
        review["sentiment"] = restapis.analyze_review_sentiments(review["review"])
    return JsonResponse({"status": 200, "reviews": reviews})


@require_GET
def get_cars(request):
    return JsonResponse(
        {
            "CarMakes": list(CarMake.objects.values("id", "name")),
            "CarModels": [
                {
                    "id": m.id,
                    "CarMake": m.car_make.name,
                    "CarModel": m.name,
                    "year": m.year,
                    "type": m.type,
                }
                for m in CarModel.objects.select_related("car_make").all()
            ],
        }
    )


@require_POST
@guarded
def add_review(request):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Sign in before posting a review."}, status=401)
    data = object_body(
        request,
        {"review": 5000, "purchase_date": 10, "car_make": 100, "car_model": 100},
    )
    dealer_id = int(data["dealership"])
    text = data["review"].strip()
    year = int(data["car_year"])
    if (
        not text
        or len(text) > 5000
        or not 2015 <= year <= 2023
        or date.fromisoformat(data["purchase_date"]) > date.today()
    ):
        return JsonResponse(
            {"error": "Enter a valid review, purchase date and car year (2015-2023)."},
            status=400,
        )
    if not restapis.get_request(f"fetchDealer/{dealer_id}"):
        return JsonResponse({"error": "Dealer not found."}, status=404)
    if not CarModel.objects.filter(
        car_make__name=data["car_make"], name=data["car_model"]
    ).exists():
        return JsonResponse({"error": "Select a valid car make and model."}, status=400)
    review = {key: data[key] for key in ["purchase_date", "car_make", "car_model"]}
    review.update(
        name=request.user.get_full_name() or request.user.username,
        dealership=dealer_id,
        review=text,
        purchase=bool(data.get("purchase", True)),
        car_year=year,
    )
    saved = restapis.post_review(review)
    return JsonResponse({"status": 200, "review": saved}, status=201)

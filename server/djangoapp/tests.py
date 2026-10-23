import json
from unittest.mock import patch
import requests
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.core.management import call_command
from .models import CarMake, CarModel


class AppTests(TestCase):
    def setUp(self):
        self.client = Client(enforce_csrf_checks=True)
        self.client.get("/djangoapp/session")
        self.user = User.objects.create_user("testdriver", password="TestOnly!Strong47")
        make = CarMake.objects.create(name="Nissan")
        CarModel.objects.create(car_make=make, name="Pathfinder", type="SUV", year=2023)

    def post(self, path, data):
        token = self.client.cookies["csrftoken"].value
        return self.client.post(
            path,
            data=json.dumps(data),
            content_type="application/json",
            HTTP_X_CSRFTOKEN=token,
        )

    def test_login_logout_server_session(self):
        response = self.post(
            "/djangoapp/login",
            {"userName": "testdriver", "password": "TestOnly!Strong47"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            self.client.get("/djangoapp/session").json()["userName"], "testdriver"
        )
        self.assertEqual(self.client.get("/djangoapp/logout").json(), {"userName": ""})
        self.assertEqual(self.client.get("/djangoapp/session").json()["userName"], "")

    def test_login_invalid_and_method(self):
        self.assertEqual(
            self.post(
                "/djangoapp/login", {"userName": "testdriver", "password": "bad"}
            ).status_code,
            401,
        )
        self.assertEqual(self.client.get("/djangoapp/login").status_code, 405)

    def test_csrf_enforced(self):
        self.assertEqual(
            self.client.post(
                "/djangoapp/login", data="{}", content_type="application/json"
            ).status_code,
            403,
        )

    def test_register_duplicate_and_password_validation(self):
        data = {
            "userName": "anotherdriver",
            "firstName": "Demo",
            "lastName": "Driver",
            "email": "demo@example.com",
            "password": "TestOnly!Strong47",
        }
        self.assertEqual(self.post("/djangoapp/register", data).status_code, 201)
        self.assertEqual(self.post("/djangoapp/register", data).status_code, 409)
        data.update(userName="weakdriver", password="1")
        self.assertEqual(self.post("/djangoapp/register", data).status_code, 400)

    def test_malformed_input_is_400(self):
        self.assertEqual(self.post("/djangoapp/login", {}).status_code, 400)

    def test_null_numeric_and_non_object_inputs_are_400(self):
        for value in [None, 42, [], {}, ""]:
            with self.subTest(value=value):
                self.assertEqual(
                    self.post("/djangoapp/register", {"userName": value}).status_code,
                    400,
                )
                self.assertEqual(self.post("/djangoapp/login", value).status_code, 400)
        self.client.force_login(self.user)
        for value in [None, 42, [], {}]:
            with self.subTest(review=value):
                self.assertEqual(
                    self.post("/djangoapp/add_review", {"review": value}).status_code,
                    400,
                )

    @patch("djangoapp.restapis.get_request")
    def test_state_and_missing_dealer(self, get):
        get.return_value = [{"id": 1, "state": "Kansas"}]
        self.assertEqual(
            self.client.get("/djangoapp/get_dealers/Kansas").json()["dealers"][0][
                "state"
            ],
            "Kansas",
        )
        get.assert_called_with("fetchDealers/Kansas")
        get.return_value = []
        self.assertEqual(self.client.get("/djangoapp/dealer/999").status_code, 404)

    @patch("djangoapp.restapis.get_request", side_effect=requests.ConnectionError())
    def test_dependency_failure_sanitized(self, get):
        response = self.client.get("/djangoapp/get_dealers")
        self.assertEqual(response.status_code, 502)
        self.assertEqual(
            response.json()["error"], "A dependent service is unavailable."
        )

    @patch("djangoapp.restapis.analyze_review_sentiments", return_value="positive")
    @patch(
        "djangoapp.restapis.get_request",
        return_value=[{"id": 1, "review": "Fantastic services"}],
    )
    def test_mocked_sentiment_contract(self, get, sentiment):
        self.assertEqual(
            self.client.get("/djangoapp/reviews/dealer/1").json()["reviews"][0][
                "sentiment"
            ],
            "positive",
        )
        sentiment.assert_called_once_with("Fantastic services")

    @patch("djangoapp.restapis.post_review")
    @patch("djangoapp.restapis.get_request", return_value=[{"id": 1}])
    def test_review_authorization_identity_and_validation(self, get, post):
        data = {
            "name": "forged",
            "dealership": 1,
            "review": "Demo review",
            "purchase": True,
            "purchase_date": "2023-03-01",
            "car_make": "Nissan",
            "car_model": "Pathfinder",
            "car_year": 2023,
        }
        self.assertEqual(self.post("/djangoapp/add_review", data).status_code, 401)
        self.client.force_login(self.user)
        post.return_value = {"id": 101}
        self.assertEqual(self.post("/djangoapp/add_review", data).status_code, 201)
        self.assertEqual(post.call_args.args[0]["name"], "testdriver")
        data["car_year"] = 1900
        self.assertEqual(self.post("/djangoapp/add_review", data).status_code, 400)

    def test_seed_idempotent(self):
        call_command("seed_cars")
        first = (CarMake.objects.count(), CarModel.objects.count())
        call_command("seed_cars")
        self.assertEqual(first, (CarMake.objects.count(), CarModel.objects.count()))
        self.assertGreater(
            len(self.client.get("/djangoapp/get_cars").json()["CarModels"]), 1
        )

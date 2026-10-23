import os
from urllib.parse import quote
import requests


def get_request(endpoint):
    response = requests.get(
        os.environ.get("BACKEND_URL", "http://127.0.0.1:3030").rstrip("/")
        + "/"
        + endpoint.lstrip("/"),
        timeout=15,
    )
    response.raise_for_status()
    return response.json()


def analyze_review_sentiments(text):
    response = requests.get(
        os.environ.get("SENTIMENT_URL", "http://127.0.0.1:5050").rstrip("/")
        + "/analyze/"
        + quote(text, safe=""),
        timeout=15,
    )
    response.raise_for_status()
    return response.json()["sentiment"]


def post_review(data):
    response = requests.post(
        os.environ.get("BACKEND_URL", "http://127.0.0.1:3030").rstrip("/")
        + "/insert_review",
        json=data,
        headers={"X-Backend-Write-Token": os.environ["BACKEND_WRITE_TOKEN"]},
        timeout=15,
    )
    response.raise_for_status()
    return response.json()

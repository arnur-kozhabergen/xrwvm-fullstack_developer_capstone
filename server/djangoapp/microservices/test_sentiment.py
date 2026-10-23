import unittest
from app import app


class SentimentTest(unittest.TestCase):
    def test_actual_bundled_vader(self):
        client = app.test_client()
        self.assertEqual(
            client.get("/analyze/Fantastic%20services").json["sentiment"], "positive"
        )
        self.assertEqual(
            client.get("/analyze/Terrible%20service").json["sentiment"], "negative"
        )
        self.assertEqual(
            client.get("/analyze/The%20car%20is%20blue").json["sentiment"], "neutral"
        )

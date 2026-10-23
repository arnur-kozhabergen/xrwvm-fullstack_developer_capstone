from pathlib import Path
from flask import Flask, jsonify
from nltk import data
from nltk.sentiment import SentimentIntensityAnalyzer

app = Flask(__name__)
# Register only this service's bundled, read-only sentiment assets.
data.path.insert(0, str(Path(__file__).resolve().parent / "sentiment"))
sia = SentimentIntensityAnalyzer(
    "vader_lexicon.zip/vader_lexicon/vader_lexicon.txt"
)


@app.get("/")
def home():
    return jsonify(service="Dealership review sentiment")


@app.get("/analyze/<path:input_txt>")
def analyze_sentiment(input_txt):
    if len(input_txt) > 5000:
        return jsonify(error="Review is too long"), 400
    score = sia.polarity_scores(input_txt)["compound"]
    return jsonify(
        sentiment=(
            "positive" if score >= 0.05 else "negative" if score <= -0.05 else "neutral"
        )
    )


if __name__ == "__main__":
    import os

    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "5050")), debug=False)

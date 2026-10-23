FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py ./
COPY sentiment/vader_lexicon.zip ./sentiment/vader_lexicon.zip
EXPOSE 5050
CMD ["sh", "-c", "gunicorn app:app --bind 0.0.0.0:${PORT:-5050} --workers 1"]

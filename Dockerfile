FROM python:3.9-slim
WORKDIR /app
COPY . /app
RUN pip install -r requirements.txt
CMD ["gunicorn", "-b", "0.0.0.0:8080", "app:app"]
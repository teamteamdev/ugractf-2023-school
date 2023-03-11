FROM python:3-alpine
WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
CMD ["gunicorn", "-b", "unix:/tmp/app.sock", "server:app"]

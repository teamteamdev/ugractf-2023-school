FROM ubuntu:22.10
RUN apt-get update && apt-get install -y gcc python3 python3-pip
RUN pip install gunicorn
WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
CMD ["gunicorn", "-b", "unix:/tmp/app.sock", "server:make_app()"]

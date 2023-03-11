FROM imachug/kyzylborda_lib
RUN pip install gunicorn
EXPOSE 8080
WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
COPY . /app/
CMD ["gunicorn", "-b", "unix:/tmp/app.sock", "server:make_app()"]

FROM python:3

EXPOSE 80
VOLUME /usr/src/app/static

WORKDIR /usr/src/app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN python3 manage.py collectstatic
RUN python3 manage.py migrate

CMD ["python3", "manage.py", "runserver", "0:80"]

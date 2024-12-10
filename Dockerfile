FROM python:3

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD python manage.py makemigrations members && python manage.py migrate members&& python manage.py migrate && python manage.py runserver 0.0.0.0:8000
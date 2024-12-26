FROM tensorflow/tensorflow:2.11.0-py3

WORKDIR /app

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app/

EXPOSE 8002

CMD ["uvicorn", "src.main:main", "--host", "0.0.0.0", "--port", "8002"]

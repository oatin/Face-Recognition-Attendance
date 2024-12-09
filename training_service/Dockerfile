FROM tensorflow/tensorflow:latest

WORKDIR /training_service

COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app","--reload"]
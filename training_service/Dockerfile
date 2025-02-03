FROM tensorflow/tensorflow:2.16.1

WORKDIR /training_service

RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    cmake

COPY requirements.txt ./
RUN pip install -r requirements.txt


COPY . .

EXPOSE 8001

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]
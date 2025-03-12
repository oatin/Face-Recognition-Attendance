
# Face-Recognition-Attendance

ระบบนี้เป็นระบบเช็คชื่อโดยใช้การจดจำใบหน้า พัฒนาโดยใช้ Docker สำหรับการจัดการคอนเทนเนอร์ของแอปพลิเคชันและฐานข้อมูล PostgreSQL โดยมีบริการหลักดังนี้:

- app: เว็บแอปพลิเคชันหลัก

- db: ฐานข้อมูล PostgreSQL

- training_service: บริการสำหรับการฝึกและอัปเดตรูปแบบโมเดล
## โครงสร้าง Docker Compose

```
services:
  app:
    build:
      context: .
      dockerfile: Dockerfile
    volumes:
      - ./media:/media
    ports:
      - "8000:8000"
    depends_on:
      - db
    environment:
      - DATABASE_URL=postgres://admin:a@db:5432/db_face_scan
    networks:
      - face_network

  db:
    image: postgres:15
    ports:
      - "5432:5432"
    volumes:
      - db_data:/var/lib/postgresql/data
    environment:
      POSTGRES_USER: admin
      POSTGRES_PASSWORD: a
      POSTGRES_DB: db_face_scan
      LANG: en_US.UTF-8
      LC_ALL: en_US.UTF-8
    networks:
      - face_network

  training_service:
    build:
      context: ./training_service
      dockerfile: Dockerfile
    volumes:
      - ./media:/media
      - ./training_service:/training_service
    ports:
      - "8001:8001"
    environment:
      - DATABASE_URL=postgres://admin:a@db:5432/db_face_scan
    depends_on:
      - db
      - app
    networks:
      - face_network

volumes:
  db_data:

networks:
  face_network:
    driver: bridge
```

## วิธีการติดตั้งและใช้งาน

ติดตั้ง Docker และ Docker Compose หากยังไม่มี ให้ติดตั้ง Docker และ Docker Compose ก่อน 

โคลนโปรเจค
```bash
git clone https://github.com/oatin/Face-Recognition-Attendance
cd Face-Recognition-Attendance
```

เรียกใช้งาน Docker Compose
```bash
docker-compose up -d --build
```

ตรวจสอบการทำงานของคอนเทนเนอร์
```bash
docker ps
```

เข้าใช้งานระบบ
- เว็บแอปพลิเคชัน: http://localhost:8000
- Training Service: http://localhost:8001

วิธีหยุดการทำงานของระบบ
```bash
docker-compose down
```
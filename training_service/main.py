from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from sqlalchemy import inspect

DATABASE_URL = "postgresql+asyncpg://admin:a@db:5432/db_face_scan"

engine = create_async_engine(DATABASE_URL, echo=True)

# สร้าง session maker
async_session = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

app = FastAPI()

# Dependency สำหรับใช้งาน session
async def get_db():
    async with async_session() as session:
        yield session

@app.get("/")
async def root():
    return {"message": "Hello, FastAPI with PostgreSQL"}

@app.get("/tables/")
async def list_tables(db: AsyncSession = Depends(get_db)):
    async with db.bind.connect() as conn:  
        tables = []
        def inspect_tables(connection):
            inspector = inspect(connection)
            for table_name in inspector.get_table_names():
                columns = inspector.get_columns(table_name)
                tables.append({
                    "table_name": table_name,
                    "columns": [{"name": col["name"], "type": str(col["type"])} for col in columns]
                })

        await conn.run_sync(inspect_tables)

    return {"tables": tables}
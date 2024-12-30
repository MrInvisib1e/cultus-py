import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

database_url = os.getenv('DATABASE_URL')
# Create an asynchronous engine
engine = create_async_engine(database_url)

# Create an asynchronous session maker
# Note: We're passing class_=AsyncSession to ensure it creates asynchronous sessions
AsyncSession = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

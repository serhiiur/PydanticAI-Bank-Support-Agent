from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from agent.core.settings import settings

engine = create_async_engine(settings.database.url, echo=settings.debug)
async_session = async_sessionmaker(engine, expire_on_commit=False)

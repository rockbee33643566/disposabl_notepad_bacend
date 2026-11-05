import asyncio

import uvicorn

from bacend import app, database
from bacend.logger import get_logger

logger = get_logger(__name__)

async def main() -> None:
    port = 8000

    await database.init_db()
    logger.info("База данных инициализирована")
    logger.info("Запуск сервера на порту %s", port)
    uvicorn.run(app=app, port=port)

if __name__ == "__main__": 
    asyncio.run(main())
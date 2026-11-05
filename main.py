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
    config = uvicorn.Config(app=app, host="0.0.0.0", port=port)
    server = uvicorn.Server(config)
    await server.serve()

if __name__ == "__main__": 
    asyncio.run(main())
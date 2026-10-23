import uvicorn

from bacend.database import get_db_connection, init_db
from bacend.api import app

def main() -> None:
    conn = get_db_connection()
    init_db(conn=conn)
    conn.close()

    uvicorn.run(app=app, port=8080)
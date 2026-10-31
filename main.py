import uvicorn

from bacend import app, database

def main() -> None:
    database.init_db()
    uvicorn.run(app=app, port=8080)

if __name__ == "__main__": 
    main()
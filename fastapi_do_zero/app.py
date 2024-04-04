from fastapi import FastAPI

from fastapi_do_zero.routes import auth, users
from fastapi_do_zero.schemas import Message

app = FastAPI()

app.include_router(auth.router)
app.include_router(users.router)


@app.get('/', status_code=200, response_model=Message)
def read_root():
    return {'message': 'Olá mundo'}

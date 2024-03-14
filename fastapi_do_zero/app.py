from fastapi import FastAPI

from fastapi_do_zero.schemas import Message, UserPublic, UserSchema

app = FastAPI()


@app.get('/', status_code=200, response_model=Message)
def read_root():
    return {'message': 'Olá mundo'}


@app.post('/users/', status_code=201, response_model=UserPublic)
def create_user(user: UserSchema):
    return user

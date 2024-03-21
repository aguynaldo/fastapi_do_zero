from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.orm import Session

from fastapi_do_zero.database import get_session
from fastapi_do_zero.models import User
from fastapi_do_zero.schemas import (
    Message,
    Token,
    UserList,
    UserPublic,
    UserSchema,
)
from fastapi_do_zero.security import (
    create_access_token,
    get_password_hash,
    verify_password,
)

app = FastAPI()


@app.get('/', status_code=200, response_model=Message)
def read_root():
    return {'message': 'Olá mundo'}


@app.post('/token', response_model=Token)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_session),
):
    user = session.scalar(select(User).where(User.email == form_data.username))

    if not user:
        raise HTTPException(status_code=400, detail='Usuário não encontrado.')

    if not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=400, detail='Usuário ou senha inválido.'
        )

    access_toke = create_access_token(data={'sub': user.email})

    return {'access_token': access_toke, 'token_type': 'bearer'}


@app.post('/users/', response_model=UserPublic, status_code=201)
def create_user(user: UserSchema, session: Session = Depends(get_session)):
    db_user = session.scalar(
        select(User).where(User.username == user.username)
    )

    if db_user:
        raise HTTPException(status_code=400, detail='Username já cadastrado.')

    hashed_password = get_password_hash(user.password)

    db_user = User(
        username=user.username, password=hashed_password, email=user.email
    )

    session.add(db_user)
    session.commit()
    session.refresh(db_user)

    return db_user


@app.get('/users/', response_model=UserList)
def read_users(
    skip: int = 0, limit: int = 100, session: Session = Depends(get_session)
):
    users = session.scalars(select(User).offset(skip).limit(limit)).all()
    return {'users': users}


@app.get('/users/{user_id}', response_model=UserPublic)
def read_user(user_id: int, session: Session = Depends(get_session)):
    user_db = session.scalar(select(User).where(User.id == user_id))

    if not user_db:
        raise HTTPException(status_code=404, detail='Usuário não encontrado.')

    return user_db


@app.put('/users/{user_id}', response_model=UserPublic)
def update_user(
    user_id: int, user: UserSchema, session: Session = Depends(get_session)
):
    db_user = session.scalar(select(User).where(User.id == user_id))

    if not db_user:
        raise HTTPException(status_code=404, detail='Usuário não encontrado.')

    db_user.username = user.username
    db_user.password = get_password_hash(user.password)
    db_user.email = user.email
    session.commit()
    session.refresh(db_user)

    return db_user


@app.delete('/users/{user_id}', response_model=Message)
def delete_user(user_id: int, session: Session = Depends(get_session)):
    user_db = session.scalar(select(User).where(User.id == user_id))

    if not user_db:
        raise HTTPException(status_code=404, detail='Usuário não encontrado.')

    session.delete(user_db)
    session.commit()

    return {'message': 'Usuário deletado com sucesso.'}

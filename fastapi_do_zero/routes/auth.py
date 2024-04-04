from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.orm import Session

from fastapi_do_zero.database import get_session
from fastapi_do_zero.models import User
from fastapi_do_zero.schemas import Token
from fastapi_do_zero.security import create_access_token, verify_password

OAuth2Form = Annotated[OAuth2PasswordRequestForm, Depends()]
Session = Annotated[Session, Depends(get_session)]
router = APIRouter(prefix='/auth', tags=['auth'])


@router.post('/token', response_model=Token)
def login_for_access_token(
    form_data: OAuth2Form,
    session: Session,
):
    user = session.scalar(select(User).where(User.email == form_data.username))

    if not user:
        raise HTTPException(status_code=400, detail='Usuário não encontrado.')

    if not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=400, detail='Usuário ou senha inválido.'
        )

    access_token = create_access_token(data={'sub': user.email})

    return {'access_token': access_token, 'token_type': 'bearer'}

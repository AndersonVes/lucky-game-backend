from typing import Union
from pydantic import BaseModel


class AuthErrorOut(BaseModel):
    detail: str


class AuthUserOut(BaseModel):
    id: int
    name: str


class AuthSuccessOut(BaseModel):
    access_token: str
    token_type: str
    user: AuthUserOut

class GoogleLoginIn(BaseModel):
    id_token: str


class FacebookLoginIn(BaseModel):
    access_token: str 

AuthOut = Union[AuthSuccessOut, AuthErrorOut]

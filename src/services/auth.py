from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from utils.env import ACCESS_TOKEN, PARTNERS_ACCESS_TOKEN

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def api_key_auth(api_key: str = Depends(oauth2_scheme)):
    if api_key != ACCESS_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Forbidden"
        )


def partners_api_key_auth(api_key: str = Depends(oauth2_scheme)):
    if api_key != PARTNERS_ACCESS_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Forbidden"
        )

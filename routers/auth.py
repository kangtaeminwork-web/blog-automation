from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from models import UserDB
from database import get_db
from auth import hash_password, verify_password, create_access_token

router = APIRouter()

@router.post("/register")
def register(username: str, password: str, email: str, db: Session = Depends(get_db)):
    if db.query(UserDB).filter(UserDB.username == username).first():
        raise HTTPException(status_code=400, detail="이미 존재하는 아이디입니다")
    user = UserDB(username=username, email=email, hashed_password=hash_password(password))
    db.add(user)
    db.commit()
    return {"message": "회원가입 완료!"}

@router.post("/token")
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(UserDB).filter(UserDB.username == form.username).first()
    if not user or not verify_password(form.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="아이디 또는 비밀번호 오류")
    token = create_access_token({"sub": user.username})
    return {"access_token": token, "token_type": "bearer"}
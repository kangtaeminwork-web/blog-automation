# Phase 7 완료 — 오늘 세션 정리

## 완료한 것

**실무 폴더 구조 리팩터링**

기존 `main.py` 하나에 모든 코드가 있던 구조를 아래처럼 분리했습니다.

```
blog-automation/
├── routers/
│   ├── __init__.py
│   ├── posts.py      ← 포스트 API
│   └── auth.py       ← 회원 API
├── database.py       ← DB 설정
├── models.py         ← 그대로
├── auth.py           ← 그대로
├── main.py           ← 라우터 등록만 담당
└── posts.db
```

**1. `database.py`**

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

DATABASE_URL = "sqlite:///./posts.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

**2. `routers/auth.py`**

```python
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
```

**3. `routers/posts.py`**

```python
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from sqlalchemy.orm import Session
from models import PostDB, UserDB
from database import get_db
from auth import decode_token

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    username = decode_token(token)
    if not username:
        raise HTTPException(status_code=401, detail="유효하지 않은 토큰")
    user = db.query(UserDB).filter(UserDB.username == username).first()
    if not user:
        raise HTTPException(status_code=401, detail="유저를 찾을 수 없습니다")
    return user

class Post(BaseModel):
    title: str
    content: str

@router.post("/posts")
def create_post(post: Post, db: Session = Depends(get_db), current_user: UserDB = Depends(get_current_user)):
    new_post = PostDB(title=post.title, content=post.content, author_id=current_user.id)
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post

@router.get("/posts")
def get_posts(db: Session = Depends(get_db)):
    return db.query(PostDB).all()

@router.get("/posts/{post_id}")
def get_post(post_id: int, db: Session = Depends(get_db)):
    post = db.query(PostDB).filter(PostDB.id == post_id).first()
    if post is None:
        raise HTTPException(status_code=404, detail="포스트를 찾을 수 없습니다")
    return post

@router.put("/posts/{post_id}")
def update_post(post_id: int, post: Post, db: Session = Depends(get_db), current_user: UserDB = Depends(get_current_user)):
    existing_post = db.query(PostDB).filter(PostDB.id == post_id).first()
    if existing_post is None:
        raise HTTPException(status_code=404, detail="포스트를 찾을 수 없습니다")
    if existing_post.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="본인 포스트만 수정할 수 있습니다")
    existing_post.title = post.title
    existing_post.content = post.content
    db.commit()
    db.refresh(existing_post)
    return existing_post

@router.delete("/posts/{post_id}")
def delete_post(post_id: int, db: Session = Depends(get_db), current_user: UserDB = Depends(get_current_user)):
    existing_post = db.query(PostDB).filter(PostDB.id == post_id).first()
    if existing_post is None:
        raise HTTPException(status_code=404, detail="포스트를 찾을 수 없습니다")
    if existing_post.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="본인 포스트만 삭제할 수 있습니다")
    db.delete(existing_post)
    db.commit()
    return {"message": f"{post_id}번 포스트가 삭제됐습니다"}
```

**4. `main.py`**

```python
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from models import Base, UserDB
from database import engine, get_db
from auth import decode_token
from routers import posts, auth

app = FastAPI()

Base.metadata.create_all(bind=engine)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    username = decode_token(token)
    if not username:
        raise HTTPException(status_code=401, detail="유효하지 않은 토큰")
    user = db.query(UserDB).filter(UserDB.username == username).first()
    if not user:
        raise HTTPException(status_code=401, detail="유저를 찾을 수 없습니다")
    return user

app.include_router(auth.router)
app.include_router(posts.router)

@app.get("/me")
def get_me(current_user: UserDB = Depends(get_current_user)):
    return {"username": current_user.username, "email": current_user.email}
```

---

## 오늘 배운 핵심 개념

**APIRouter** — `app` 대신 `router` 로 API 조각을 만들고 나중에 `main.py` 에서 `include_router` 로 붙이는 방식

**include_router** — 레고 블록처럼 라우터 조각을 `app` 에 끼우는 역할

**yield** — `return` 과 달리 값을 넘겨주고 잠깐 멈췄다가 요청이 끝나면 돌아와서 나머지 코드 실행. DB 연결 열고 닫을 때 사용

**HTTP 메서드** — `post` 생성, `get` 조회, `put` 수정, `delete` 삭제

---

## 현재 문제점

`get_current_user` 함수가 `main.py` 와 `routers/posts.py` 에 중복으로 존재 → 나중에 `dependencies.py` 로 분리하면 깔끔해짐

---

## 다음 단계 예정

**Phase 8 — 배포 (Render / Railway)**

로컬에서만 돌아가는 API를 실제 서버에 올려서 외부에서 접근 가능하게 만들기
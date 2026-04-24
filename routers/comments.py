from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from sqlalchemy.orm import Session
from models import CommentDB, PostDB, UserDB
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

class Comment(BaseModel):
    content: str

@router.post("/posts/{post_id}/comments")
def create_comment(post_id: int, comment: Comment, db: Session = Depends(get_db), current_user: UserDB = Depends(get_current_user)):
    post = db.query(PostDB).filter(PostDB.id == post_id).first()
    if post is None:
        raise HTTPException(status_code=404, detail="포스트를 찾을 수 없습니다")
    new_comment = CommentDB(content=comment.content, author_id=current_user.id, post_id=post_id)
    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)
    return new_comment

@router.get("/posts/{post_id}/comments")
def get_comments(post_id: int, db: Session = Depends(get_db)):
    post = db.query(PostDB).filter(PostDB.id == post_id).first()
    if post is None:
        raise HTTPException(status_code=404, detail="포스트를 찾을 수 없습니다")
    return db.query(CommentDB).filter(CommentDB.post_id == post_id).all()

@router.delete("/posts/{post_id}/comments/{comment_id}")
def delete_comment(post_id: int, comment_id: int, db: Session = Depends(get_db), current_user: UserDB = Depends(get_current_user)):
    comment = db.query(CommentDB).filter(CommentDB.id == comment_id, CommentDB.post_id == post_id).first()
    if comment is None:
        raise HTTPException(status_code=404, detail="댓글을 찾을 수 없습니다")
    if comment.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="본인 댓글만 삭제할 수 있습니다")
    db.delete(comment)
    db.commit()
    return {"message": f"{comment_id}번 댓글이 삭제됐습니다"}
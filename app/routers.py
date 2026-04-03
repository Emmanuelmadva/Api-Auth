from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer
from .db import SessionLocal, engine, Base
from .model import User
from .schema import UserCreate, UserLogin, UserResponse, Token
from .utils import hash_password, verify_password, create_access_token, decode_access_token

Base.metadata.create_all(bind=engine)

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")
# Dependences
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Enregistrement des utilisateurs
@router.post("/register", response_model=UserResponse)
def register(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="L'email est invalide ou déja utiliser")
    hashed_pw = hash_password(user.password)
    new_user = User(email=user.email, password_hash=hashed_pw, full_name=user.full_name, role=user.role)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

# Login
@router.post("/login", response_model=Token)
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user or not verify_password(user.password, db_user.password_hash):
        raise HTTPException(status_code=401, detail="Vos identifiants ne sont pas correctes")
    token = create_access_token({"user_id": db_user.id, "role": db_user.role})
    return {"access_token": token, "token_type": "bearer"}

# Qui est connecter ?
@router.get("/me", response_model=UserResponse)
def read_me(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Le token est invalide")
    user = db.query(User).filter(User.id == payload["user_id"]).first()
    return user
import sqlite3
import bcrypt
from fastapi import FastAPI, HTTPException,APIRouter
from pydantic import BaseModel
import jwt
from dotenv import load_dotenv
import os
from database import get_database

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")
router = APIRouter()

with sqlite3.connect(get_database()) as conn:
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY,
            login TEXT,
            password_hash TEXT,
            role TEXT
        )
""")
    cursor.execute("""
    CREATE UNIQUE INDEX IF NOT EXISTS idx_users_login
    ON users(login)
""")
    
class User(BaseModel):
    login : str
    password : str

def create_token(user_id,login,role):
    payload = {"user_id":user_id,"login":login,"role":role}
    token = jwt.encode(payload,SECRET_KEY,algorithm="HS256")
    return token


def verify_token(token):
    try:
        decoded = jwt.decode(token,algorithms=["HS256"],key=SECRET_KEY)
        return decoded
    except Exception:
        raise HTTPException(status_code=401,detail="Invalid or expired token")


@router.post("/users")
def create_login(user : User):
    hashed_password = bcrypt.hashpw(user.password.encode(), bcrypt.gensalt()).decode()

    with sqlite3.connect(get_database()) as conn:
        cursor = conn.cursor()
        
        cursor.execute("SELECT login FROM users WHERE login = ?",(user.login,) )
        data = cursor.fetchone()
        if data is None:
            cursor.execute("INSERT INTO users (login,password_hash,role) VALUES (?,?,?) ",(user.login,hashed_password,"user"))
            conn.commit()
            return "User Created"
        else:
            raise HTTPException(status_code=409,detail="User already in our system")

@router.post("/login")
def login(user : User):
    with sqlite3.connect(get_database()) as conn:
        cursor = conn.cursor()

        cursor.execute("SELECT id,password_hash,role FROM users WHERE login = ?",(user.login,))
        data = cursor.fetchone()
        if data is None:
           raise HTTPException(status_code=401, detail="User or Password invalid")
        elif bcrypt.checkpw(user.password.encode(),data[1].encode()):
            token = create_token(data[0],user.login,data[2])
            return {"token_type": "Bearer","access_token": token}
        else:
            raise HTTPException(status_code=401,detail="User or Password invalid")
            

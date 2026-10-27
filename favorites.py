import sqlite3
from fastapi import FastAPI, HTTPException,APIRouter,Depends,Header
from pydantic import BaseModel
from users import verify_token
from request import get_recommendation,get_artist_info
from database import get_database

router = APIRouter()

with sqlite3.connect(get_database()) as conn:
    cursor = conn.cursor()

    cursor.execute("""
            CREATE TABLE IF NOT EXISTS favorites(
                id INTEGER PRIMARY KEY,
                user_id INTEGER NOT NULL,
                artist_id TEXT NOT NULL,
                artist_name TEXT NOT NULL,
                UNIQUE(user_id,artist_id)
            )
""")

def auth(authorization: str = Header()):
    token = authorization[7:]
    return verify_token(token)


def admin_auth(authorization: str = Header()):
    token = authorization[7:]
    decoded = verify_token(token)

    if decoded["role"] == "admin":
        return decoded

    raise HTTPException(status_code=403, detail="Forbidden")

class Favorite(BaseModel):
    artist_name : str

class Favorite_response(BaseModel):
    artist_name : str
    artist_id : str

@router.post("/users/me/favorites")
def post_favorites(favorite : Favorite , user = Depends(auth)):
    user_id = user["user_id"]
    with sqlite3.connect(get_database()) as conn:
        cursor = conn.cursor()
        # cursor.execute("SELECT COUNT (*) FROM favorites WHERE user_id = ?",(favorite.user_id,))
        # data = cursor.fetchone()[0]
        # if data >= 5:
        #     raise HTTPException(status_code=400,detail="Already have 5 songs")
        try:
            chosen_artist = get_artist_info(favorite.artist_name)
        except:
            raise HTTPException(status_code=404,detail="Band not found")
        else:
            artist_id = chosen_artist["id"]
            artist_name = chosen_artist["name"]

        cursor.execute("SELECT artist_id FROM favorites WHERE user_id = ?",(user_id,))
        band_list = [band[0] for band in cursor.fetchall()]
        if artist_id not in band_list:
            cursor.execute("INSERT INTO favorites (user_id,artist_id,artist_name) VALUES (?,?,?)",(user_id,artist_id,artist_name))
            conn.commit()
        else:
            raise HTTPException(status_code=409,detail="Artist already included")
        
@router.get("/users/me/favorites")
def get_favorites(user = Depends(auth)):
    user_id = user["user_id"]
    with sqlite3.connect(get_database()) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor() 
        cursor.execute("SELECT * FROM favorites WHERE user_id = ?",(user_id,))
        data = [dict(row) for row in cursor.fetchall()]
        return data

@router.delete("/users/me/favorites/{favorite_id}")
def delete_favorite(favorite_id,user = Depends(auth)):
    user_id = user["user_id"]
    with sqlite3.connect(get_database()) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM favorites WHERE id = ? AND user_id = ?", (favorite_id,user_id))
        result = cursor.fetchone()
        if result is None:
            raise HTTPException(status_code=404, detail="Not found")
        cursor.execute("DELETE FROM favorites WHERE id = ? AND user_id = ?",(favorite_id,user_id))
        conn.commit()
        return "Band Deleted"

def get_favorites_db(user_id: int,user = Depends(auth)):
    with sqlite3.connect(get_database()) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor() 
        cursor.execute("SELECT * FROM favorites WHERE user_id = ?",(user_id,))
        data = [dict(row) for row in cursor.fetchall()]
        return data
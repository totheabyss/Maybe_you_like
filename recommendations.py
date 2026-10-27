import sqlite3
from fastapi import FastAPI, HTTPException,APIRouter,Depends,Header
from pydantic import BaseModel
import random
from request import get_recommendation
from favorites import get_favorites_db
from database import get_database
from favorites import auth

router = APIRouter()

with sqlite3.connect(get_database()) as conn:
    cursor = conn.cursor()

    cursor.execute("""
            CREATE TABLE IF NOT EXISTS recommendations(
                id INTEGER PRIMARY KEY,
                user_id INTEGER NOT NULL,
                artist_id TEXT NOT NULL,
                artist_name TEXT NOT NULL,
                recommended_at TEXT DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id,artist_id)
            )
""")


@router.get("/users/me/recommendations")
def get_recommendations(user=Depends(auth)):
    user_id = user["user_id"]
    bands = get_favorites_db(user_id)
    with sqlite3.connect(get_database()) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT artist_id FROM recommendations WHERE user_id = ?",(user_id,))
        already_in_db = [row["artist_id"] for row in cursor.fetchall()]
        bands_id = [row["artist_id"] for row in bands]
        
        new_bands = [band for band in bands_id if band not in already_in_db]
        if new_bands == []:
            raise HTTPException(status_code=409, detail="No bands to recommend,\n add some more bands to get more results")
        random_band = random.choice(new_bands)
        chosen_band = [band['artist_name'] for band in bands if random_band in band["artist_id"]]
        chosen_band = chosen_band[0]
        recommendations = get_recommendation(chosen_band)
        filtered_band = []
        for recommendation in recommendations:
            if recommendation["id"] not in already_in_db and recommendation["id"] not in bands_id:
                filtered_band.append(recommendation)
        
        if not filtered_band:
            raise HTTPException(status_code=404,detail="No new recommendations available")

        maybe_you_like = random.choice(filtered_band)
        return maybe_you_like

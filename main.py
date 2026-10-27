from fastapi import FastAPI
from favorites import router as music_router
from users import router as user_router
from recommendations import router as recomends_router
app = FastAPI()

app.include_router(music_router)
app.include_router(user_router)
app.include_router(recomends_router)
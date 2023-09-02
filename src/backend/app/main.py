from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import summoners, banpick, mastery
from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend
from fastapi_cache.decorator import cache

app = FastAPI()

origins = [
    "http://de-4-2-vue.s3-website.ap-northeast-3.amazonaws.com",
    "d1rxnfuwcw8lzd.cloudfront.net",
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(summoners.router)
app.include_router(banpick.router)
app.include_router(mastery.router)


def cache_config():
    FastAPICache.init(InMemoryBackend(), prefix="inmemory:")


@app.on_event("startup")
async def on_startup():
    cache_config()


@app.get("/")
async def root():
    return {"message": "Hello Bigger Applications!"}



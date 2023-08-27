from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import summoners, banpick

# app = FastAPI(dependencies=[Depends(get_query_token)])
app = FastAPI()

origins = [
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


@app.get("/")
async def root():
    return {"message": "Hello Bigger Applications!"}

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from internal.routers import summoners, team

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
app.include_router(team.router)


@app.get("/")
async def root():
    return {"message": "Hello Bigger Applications!"}

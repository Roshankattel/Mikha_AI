from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from routers import face_recognition, face_anti_spoof, sign_verify

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(face_recognition.router)
app.include_router(face_anti_spoof.router)
app.include_router(sign_verify.router)

if __name__ == "__main__":
    uvicorn.run(app, port=5500, debug=True)

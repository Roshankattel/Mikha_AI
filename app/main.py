from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import id_extractor
# import uvicorn
from .routers import face_recognition, face_anti_spoof, sign_verify, mrz_passport, id_extractor

description = """
APP helps you to call all AI APIs . 🚀

## Items

* **Facial Recogniton** .
* **Face Anti-Spoof Checker**.
* **Signature Exraction/Verification**.
* **Passport MRZ Reader**.
* **ID extractor**.
"""

app = FastAPI(title="Bitskraft AI App", description=description, version="0.1")

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
app.include_router(mrz_passport.router)
app.include_router(id_extractor.router)



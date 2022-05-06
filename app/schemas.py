from pydantic import BaseModel
from typing import Optional


class FaceDetect(BaseModel):
    face_detect: bool
    no_of_person: int
    mood:  Optional[str] = None
    landmark_image: Optional[str] = None


class FaceRecog(BaseModel):
    similar: bool
    similarity_score: float
    match_index: int
    no_of_person: int
    original_image: str
    landmark_image: Optional[str] = None


class FaceSpoof(BaseModel):
    real: bool
    score: float
    pred_time: float
    result_image: Optional[str] = None


class SignDetect(BaseModel):
    sign_detect: bool
    no_of_sign: int


class SignExtract(BaseModel):
    pred_score: float
    extracted_image: str


class SignCompare(BaseModel):
    sim_score: float
    similar: bool


class SignCheck(BaseModel):
    id: str
    sim_score: float
    similar: bool
    ref_image: str


class SignVerify(BaseModel):
    id: str
    pred_score: float
    sim_score: float
    similar: bool
    ref_image: str
    extracted_image: str


class FaceExpress(BaseModel):
    mood: str

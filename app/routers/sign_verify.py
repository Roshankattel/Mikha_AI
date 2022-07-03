from typing import Optional
from fastapi import HTTPException, File, Form,status,APIRouter
from fastapi.datastructures import UploadFile
from .. import schemas,utils
import glob

from ..sign_verify.signver.src import sign_process

from ..config import settings

INPUT_FILE = f"{settings.sign_file_input_path}"
EXTRACT_SIGN = f"{settings.sign_extract_path}"
INPUT_SIGN = f"{settings.sign_input_path}"
REFERENCE_SIGN = f"{settings.sign_reference_path}"
router = APIRouter(
    prefix="/signature",
    tags=['Signature Verification']
)

@router.post("/detector", response_model=schemas.SignDetect, status_code=status.HTTP_200_OK)
async def detect(image: UploadFile = File(...)):
    utils.save_image(INPUT_FILE+image.filename, image.file)
    signatures = sign_process.detect_sign(image.filename)
    detection = bool(signatures)
    return {"sign_detect": detection, "no_of_sign": signatures}


@ router.post("/extractor", response_model=schemas.SignExtract, status_code=status.HTTP_200_OK)
async def extract(image: UploadFile = File(...), clean: Optional[bool] = True):
    utils.save_image(INPUT_FILE+image.filename, image.file)
    predScore = sign_process.extract_sign(image.filename, clean)
    if(predScore == 0):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid Image, No signatures Found")

    encoded_image = utils.img_to_base64(EXTRACT_SIGN+image.filename)
    return {"pred_score": float(predScore), "extracted_image": encoded_image}


@ router.post("/comparer", response_model=schemas.SignCompare, status_code=status.HTTP_200_OK)
async def compare(imagea: UploadFile = File(...), imageb: UploadFile = File(...), clean: Optional[bool] = False):
    utils.save_image(INPUT_SIGN+imagea.filename, imagea.file)
    utils.save_image(INPUT_SIGN+imageb.filename, imageb.file)
    sim, simScore = sign_process.compare(INPUT_SIGN+imagea.filename, INPUT_SIGN+imageb.filename, clean)
    return {"sim_score": float(simScore), "similar": sim}


@router.post("/checker", response_model=schemas.SignCheck, status_code=status.HTTP_200_OK)
async def check(image: UploadFile = File(...), id: str = Form(...), clean: Optional[bool] = False):
    utils.save_image(INPUT_SIGN+image.filename, image.file)
    originalImagePath = (glob.glob((f"{REFERENCE_SIGN}{id}*")))
    if not originalImagePath:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Image not found")

    if (len(originalImagePath) > 1):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Multiple Reference Image found")

    sim, simScore = sign_process.compare(INPUT_SIGN+image.filename, originalImagePath[0], clean)
    encodedImage = utils.img_to_base64(originalImagePath[0])
    return {"sim_score": float(simScore), "ref_image": encodedImage, "similar": sim, "id": id}
  


@router.post("/verifyer", response_model=schemas.SignVerify, status_code=status.HTTP_200_OK)
async def verify(image: UploadFile = File(...), id: str = Form(...), clean: Optional[bool] = True):
    utils.save_image(INPUT_FILE+image.filename, image.file)
    originalImagePath = (glob.glob((f"{REFERENCE_SIGN}{id}*")))
    if not originalImagePath:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Image not found")

    if (len(originalImagePath) > 1):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Multiple Reference Image found")
    print(originalImagePath[0])

    predScore =sign_process.extract_sign(image.filename, False)
    
    if (predScore==0):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Signature not found in Image")

    sim, simScore = sign_process.compare(
        EXTRACT_SIGN+image.filename, originalImagePath[0], clean)
    encodedRefImg = utils.img_to_base64(originalImagePath[0])
    encodedExtractImg = utils.img_to_base64(EXTRACT_SIGN+image.filename)
    return {"sim_score": float(simScore), "pred_score": predScore, "ref_image": encodedRefImg, "extracted_image": encodedExtractImg, "similar": sim, "id": id}
  
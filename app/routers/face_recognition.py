from typing import Optional
from fastapi import APIRouter, File, Form, HTTPException, Depends, status
from fastapi.datastructures import UploadFile
import glob
from .. import schemas,utils
from ..face_recogn.src import face_details
# import auth
from ..config import settings

ORIGINAL_IMAGE = f"{settings.face_original_path}"
VERIFY_IMAGE = f"{settings.face_verify_path}"
LANDMARK_IMAGE = f"{settings.face_landmark_path}"
DOWNLOAD_IMAGE = f"{settings.face_download_path}"

# IDToken=Depends(auth.authenticate_user)

router = APIRouter(prefix="/face", tags=["Facial Recognition"])


@ router.post("/detection", response_model=schemas.FaceDetect, status_code=status.HTTP_200_OK)
async def face_detect(image: UploadFile=File(...), facial_landmarks: Optional[bool]=False):
    utils.save_image(VERIFY_IMAGE + image.filename, image.file)
    unknownEncoding=face_details.find_encoding(f"{VERIFY_IMAGE}/{image.filename}")
    faceCount=len(unknownEncoding)
    detection = faceCount != 0
    result={"face_detect": detection, "no_of_person": faceCount}
    if (faceCount == 1):
        predictedEmotion=face_details.face_emotion(VERIFY_IMAGE + image.filename)
        result["mood"] = predictedEmotion
        if facial_landmarks:
            imgLandmarks=face_details.find_landmarks(f"{VERIFY_IMAGE}/{image.filename}")
            imgLandmarks.save(LANDMARK_IMAGE + image.filename)
            encodedLandmarkImage=utils.img_to_base64(LANDMARK_IMAGE + image.filename)
            result["landmark_image"] = encodedLandmarkImage
    return result


@ router.post("/verification-id", response_model=schemas.FaceRecog, status_code=status.HTTP_200_OK)
async def verify_ID(image: UploadFile=File(...), id: str=Form(...), facial_landmarks: Optional[bool]=False):
    utils.save_image(VERIFY_IMAGE + image.filename, image.file)
    unknownEncoding = face_details.find_encoding(f'{VERIFY_IMAGE}/{image.filename}')
    if not unknownEncoding:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Invalid Image!, Please make sure face is visible in the image")

    originalImagePath=glob.glob((f"{ORIGINAL_IMAGE}{id}*"))
    print(originalImagePath[0])
    if not originalImagePath:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reference Image not found")

    if (len(originalImagePath)) > 1:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Multiple Reference Image found")

    return face_details.verify(image.filename,originalImagePath,facial_landmarks)

@ router.post("/verification-url", response_model=schemas.FaceRecog, status_code=status.HTTP_200_OK)
async def verify_URL(image: UploadFile=File(...), URL: str=Form(...), facial_landmarks: Optional[bool]=False,):
    result={}
    utils.save_image(VERIFY_IMAGE + image.filename, image.file)
    refImage="refImage.jpg"
    downloadStatus = utils.download_file(DOWNLOAD_IMAGE, URL, refImage)
    
    if( downloadStatus==False):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail="Image cannot be downloaded! Please check the URL")
  
    unknownEncoding = face_details.find_encoding(f'{VERIFY_IMAGE}/{image.filename}')
    
    if not unknownEncoding:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Invalid Image!, Please make sure face is visible in the upload image")
    
    originalImagePath=glob.glob((f"{DOWNLOAD_IMAGE}{refImage}"))
    
    if not originalImagePath:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reference Image not found")
    
    if (len(originalImagePath)) > 1:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Multiple Reference Image found")
    
    knownEncoding = face_details.find_encoding(f'{originalImagePath[0]}')

    if not knownEncoding:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Invalid Image!, Please make sure face is visible in the referece/URL image")

    result = face_details.verify(image.filename,originalImagePath,facial_landmarks)
    return result


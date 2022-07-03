from fastapi import status,HTTPException, File,Form,APIRouter
from fastapi.datastructures import UploadFile
from typing import Optional
from ..id_extractor import OCR 
from .. import schemas,utils
from ..config import settings

INPUT_IMAGE = f"{settings.id_extractor_input_path}"

router = APIRouter(prefix="/ocr")
    
@router.post("/extraction",response_model=schemas.OcrExtract,status_code=status.HTTP_200_OK, tags=['OCR Extraction'])
def extract_upload(image: UploadFile = File(...), language: Optional[str] = None):
    utils.save_image(INPUT_IMAGE+image.filename, image.file)
    return OCR.process_id_extract(INPUT_IMAGE+image.filename,True,False,language)

@router.post("/extraction-url",response_model=schemas.OcrExtract,status_code=status.HTTP_200_OK, tags=['OCR Extraction'])
def extract_URL(URL: str = Form(...), language: Optional[str] = None):
    downloadSuccess=utils.download_file(INPUT_IMAGE,URL,"download.jpg")
    if not (downloadSuccess):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Image cannot be downloaded! Please check the URL")
    return OCR.process_id_extract(f"{INPUT_IMAGE}download.jpg", True, False, language)

@router.post("/extraction/id",response_model=schemas.IdExtract,status_code=status.HTTP_200_OK, tags=['Bangla NID Extraction'])
def id_extract_upload(image: UploadFile = File(...), raw_data: Optional[bool] = False):
    utils.save_image(INPUT_IMAGE+image.filename, image.file)
    return OCR.process_id_extract(INPUT_IMAGE+image.filename,raw_data,True)

@router.post("/extraction-url/id",response_model=schemas.IdExtract,status_code=status.HTTP_200_OK, tags=['Bangla NID Extraction'])
def id_extract_url(URL: str = Form(...), raw_data: Optional[bool] = False):
    downloadSuccess = utils.download_file(INPUT_IMAGE,URL,"download.jpg")
    if not (downloadSuccess):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Image cannot be downloaded! Please check the URL")
    return OCR.process_id_extract(f"{INPUT_IMAGE}download.jpg", raw_data, True)
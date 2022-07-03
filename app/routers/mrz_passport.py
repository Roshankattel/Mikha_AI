
from fastapi import APIRouter, File ,  status, UploadFile,APIRouter
from .. import utils,schemas
from ..config import settings
from .id_extractor import OCR

INPUT_IMAGES= f"{settings.mrz_input_path}"

router = APIRouter(prefix="/mrz", tags=['MRZ Reader'])

@router.post("/mrz-reader", response_model=schemas.MrzReader, status_code=status.HTTP_200_OK)
async def extract(image: UploadFile = File(...)):
    utils.save_image(INPUT_IMAGES+image.filename,image.file)
    input_image =  utils.grey_scale(f"{INPUT_IMAGES}{image.filename}")
    return OCR.mrz_parser(input_image)
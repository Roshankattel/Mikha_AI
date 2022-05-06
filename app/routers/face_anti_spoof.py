import os
import cv2
import numpy as np
import argparse
import warnings
import time
from typing import Optional
from fastapi import File,  HTTPException, APIRouter
from fastapi.datastructures import UploadFile


import schemas
import utils
from config import settings

from face_spoof.src.anti_spoof_predict import AntiSpoofPredict
from face_spoof.src.generate_patches import CropImage
from face_spoof.src.utility import parse_model_name
warnings.filterwarnings('ignore')


INPUT_IMAGE = f"{settings.spoof_input_path}"
RESULT_IMAGE = f"{settings.spoof_result_path}"


router = APIRouter(prefix="/face/anti-spoof", tags=['Facial Anti-Spoofing'])


def check_image(image):
    height, width, channel = image.shape
    if width / height == 3 / 4:
        return True
    print("Image is not appropriate!!!\nHeight/Width should be 4/3.")
    return False


def test(image_name, model_dir, device_id):
    test_result = {}
    model_test = AntiSpoofPredict(device_id)
    image_cropper = CropImage()
    image = cv2.imread(INPUT_IMAGE+image_name)
    check_image_result = check_image(image)
    if check_image_result is False:
        test_result = {"img_valid": check_image_result}
        return test_result
    # resize image
    image = cv2.resize(image, (480, 640), interpolation=cv2.INTER_AREA)

    image_bbox = model_test.get_bbox(image)
    prediction = np.zeros((1, 3))
    test_speed = 0
    # sum the prediction from single model's result
    for model_name in os.listdir(model_dir):
        h_input, w_input, model_type, scale = parse_model_name(model_name)
        param = {
            "org_img": image,
            "bbox": image_bbox,
            "scale": scale,
            "out_w": w_input,
            "out_h": h_input,
            "crop": True,
        }
        if scale is None:
            param["crop"] = False
        img = image_cropper.crop(**param)
        start = time.time()
        prediction += model_test.predict(img,
                                         os.path.join(model_dir, model_name))
        test_speed += time.time()-start

    # draw result of prediction
    label = np.argmax(prediction)
    value = prediction[0][label]/2
    real = False
    if label == 1:
        real = True
        print("Image '{}' is Real Face. Score: {:.2f}.".format(image_name, value))
        result_text = "RealFace Score: {:.2f}".format(value)
        color = (255, 0, 0)
    else:
        print("Image '{}' is Fake Face. Score: {:.2f}.".format(image_name, value))
        result_text = "FakeFace Score: {:.2f}".format(value)
        color = (0, 0, 255)
    print("Prediction cost {:.2f} s".format(test_speed))
    cv2.rectangle(
        image,
        (image_bbox[0], image_bbox[1]),
        (image_bbox[0] + image_bbox[2], image_bbox[1] + image_bbox[3]),
        color, 2)
    cv2.putText(
        image,
        result_text,
        (image_bbox[0], image_bbox[1] - 5),
        cv2.FONT_HERSHEY_COMPLEX, 0.5*image.shape[0]/1024, color)

    format_ = os.path.splitext(image_name)[-1]
    result_image_name = image_name.replace(format_, "_result" + format_)
    cv2.imwrite(RESULT_IMAGE + result_image_name, image)
    test_result = {"img_valid": check_image_result, "real": real, "score": round(
        value, 3), "pred_time": round(test_speed, 3), "img": result_image_name}
    return test_result


@router.post("/", response_model=schemas.FaceSpoof, status_code=200)
async def check(image: UploadFile = File(...), result_img: Optional[bool] = False):

    utils.save_image(INPUT_IMAGE+image.filename, image.file)
    desc = "Spoof test"
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument(
        "--device_id",
        type=int,
        default=0,
        help="which gpu id, [0/1/2/3]")
    parser.add_argument(
        "--model_dir",
        type=str,
        default="./app/face_spoof/resources/anti_spoof_models",
        help="model_lib used to test")
    parser.add_argument(
        "--image_name",
        type=str,
        default=image.filename,
        help="image used to test")
    print(parser)
    args = parser.parse_args()
    test_result = test(args.image_name, args.model_dir, args.device_id)
    if not test_result["img_valid"]:
        raise HTTPException(
            status_code=400, detail="Image resolution not supported. Height/Width ratio should be 4/3")

    result = {"real": test_result["real"], "score": test_result["score"]*100,"pred_time": test_result["pred_time"]}
    if result_img:
        encoded_result_image = utils.img_to_base64(RESULT_IMAGE+test_result["img"])
        result["result_image"] = encoded_result_image
    return (result)

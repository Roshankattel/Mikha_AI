import numpy as np
import tensorflow as tf
import matplotlib.pyplot as plt
import cv2
from PIL import Image

from config import settings

INPUT_FILE = f"{settings.sign_input_path}"
EXTRACT_SIGN = f"{settings.sign_extract_path}"
INPUT_SIGN = f"{settings.sign_input_path}"
REFERENCE_SIGN = f"{settings.sign_reference_path}"

from sign_verify.signver.detector import Detector
from sign_verify.signver.cleaner import Cleaner
from sign_verify.signver.extractor import MetricExtractor
from sign_verify.signver.matcher import Matcher
from sign_verify.signver.utils import data_utils
from sign_verify.signver.utils.data_utils import  resnet_preprocess
from sign_verify.signver.utils.visualization_utils import  get_image_crops

detector_model_path = f"{settings.sign_detector_model_path}"
detector = Detector()
detector.load(detector_model_path)

extractor_model_path = f"{settings.sign_extractor_model_path}"
extractor = MetricExtractor()
extractor.load(extractor_model_path)

cleaner_model_path = f"{settings.sign_cleaner_model_path}"
cleaner = Cleaner()
cleaner.load(cleaner_model_path)

def covert_greyscale(imgPath):
    originalImage = cv2.imread(imgPath)
    grayImage = cv2.cvtColor(originalImage, cv2.COLOR_BGR2GRAY)
    cv2.imwrite(imgPath, grayImage)


def detect_sign(imgName):
    imgPath = INPUT_FILE + imgName
    covert_greyscale(imgPath)
    invertedImageNp = data_utils.img_to_np_array(imgPath, invert_image=True)
    imgTensor = tf.convert_to_tensor(invertedImageNp)
    imgTensor = imgTensor[tf.newaxis, ...]
    boxes, scores, classes, detections = detector.detect(imgTensor)
    signatures = get_image_crops(
        invertedImageNp, boxes, scores,  threshold=0.22)
    return (len(signatures))


def extract_sign(imgName, clean):
    score = 0
    imgPath = INPUT_FILE + imgName
    covert_greyscale(imgPath)
    invertedImageNp = data_utils.img_to_np_array(imgPath, invert_image=True)
    imgTensor = tf.convert_to_tensor(invertedImageNp)
    imgTensor = imgTensor[tf.newaxis, ...]
    boxes, scores, classes, detections = detector.detect(imgTensor)
    signatures = get_image_crops(
        invertedImageNp, boxes, scores,  threshold=0.22)
    if(len(signatures) > 0):
        sigs = [resnet_preprocess(x, resnet=False) for x in signatures]
        if (clean):
            norm_sigs = [x * (1./255) for x in sigs]
            sigs = cleaner.clean(np.array(norm_sigs))
            plt.imsave(EXTRACT_SIGN+imgName, sigs[0])
        else:
            image = Image.fromarray(np.uint8(sigs[0]))
            image.save(EXTRACT_SIGN+imgName)
        score = (round(scores[0], 4)*100)
    return (score)


def compare(imagea, imageb, clean):
    sim = False
    imgPaths = [imagea, imageb]
    [covert_greyscale(imgPath) for imgPath in imgPaths]
    invertedImageNp = [data_utils.img_to_np_array(
        x, invert_image=True) for x in imgPaths]
    sigs = [resnet_preprocess(x, resnet=False) for x in invertedImageNp]
    if(clean):
        norm_sigs = [x * (1./255) for x in sigs]
        cleaned_sigs = cleaner.clean(np.array(norm_sigs))
        feats = extractor.extract(cleaned_sigs)
    else:
        feats = extractor.extract(np.array(sigs) / 255)
    matcher = Matcher()
    distance = matcher.cosine_distance(feats[0], feats[1])
    similarity = round((1 - distance), 4)
    if(similarity > 1):
        similarity = 1
    elif similarity < 0:
        similarity = 0
    if (distance < 0.2):
        sim = True
    return(sim, (similarity)*100)
from turtle import distance
import face_recognition
import cv2
from PIL import Image, ImageDraw
import numpy as np
import math
import utils
import base64
import mediapipe as mp


ORIGINAL_IMAGE = "./images/face_recognition/original/"
VERIFY_IMAGE = "./images/face_recognition/verify/"
LANDMARK_IMAGE = "./images/face_recognition/landmarks/"
DOWNLOAD_IMAGE = "./images/face_recognition/download/"

GREEN = "#32CD32"  # lime green
MODEL_TOLERANCE = 0.45 

EMOTION_MODEL = "./app/face_recogn/model/emotion-ferplus-8.onnx"

emotions = ['Neutral', 'Happy', 'Surprise',
            'Sad', 'Anger', 'Disgust', 'Fear', 'Contempt']


def find_encoding(imagePath):
    imgFile = cv2.imread(imagePath)
    Img = cv2.cvtColor(imgFile, cv2.COLOR_BGR2RGB)
    return face_recognition.face_encodings(Img)


def find_landmarks(img):
    imgFile = cv2.imread(img)
    h,w,_=imgFile.shape
    if h<=1280 and w <=720:
        pil_image = lower_res_face_detect(img)
    else:
        mp_face_mesh = mp.solutions.face_mesh
        # Load drawing_utils and drawing_styles
        mp_drawing = mp.solutions.drawing_utils 
        mp_drawing_styles = mp.solutions.drawing_styles         
        # Run MediaPipe Face Mesh.
        with mp_face_mesh.FaceMesh(
            static_image_mode=True,
            refine_landmarks=True,
            max_num_faces=2,
            min_detection_confidence=0.5) as face_mesh:
            # Convert the BGR image to RGB and process it with MediaPipe Face Mesh.
            results = face_mesh.process(cv2.cvtColor(imgFile, cv2.COLOR_BGR2RGB))

            face_landmarks =  results.multi_face_landmarks[0]
            mp_drawing.draw_landmarks(
            image=imgFile,
            landmark_list=face_landmarks,
            connections=mp_face_mesh.FACEMESH_TESSELATION,
            landmark_drawing_spec=None,
            connection_drawing_spec=mp_drawing_styles
            .get_default_face_mesh_tesselation_style())
            mp_drawing.draw_landmarks(
            image=imgFile,
            landmark_list=face_landmarks,
            connections=mp_face_mesh.FACEMESH_CONTOURS,
            # landmark_drawing_spec=None,
            landmark_drawing_spec=mp_drawing.DrawingSpec(color =(0,255,0)),
            connection_drawing_spec=mp_drawing_styles
            .get_default_face_mesh_contours_style())
            mp_drawing.draw_landmarks(
            image=imgFile,
            landmark_list=face_landmarks,
            connections=mp_face_mesh.FACEMESH_IRISES,
            landmark_drawing_spec=None,
            connection_drawing_spec=mp_drawing_styles
            .get_default_face_mesh_iris_connections_style())
            imgFile= cv2.cvtColor(imgFile,cv2.COLOR_BGR2RGB)
            pil_image=Image.fromarray(imgFile)
    return(pil_image)


# TODO Rename this here and in `find_landmarks`
def lower_res_face_detect(img):
    image = face_recognition.load_image_file(img)
    stroke1 = math.ceil(image.size/1000000)
    stroke1 = min(stroke1, 10)

    face_landmarks_list = face_recognition.face_landmarks(image)

    result = Image.fromarray(image)
    d = ImageDraw.Draw(result)

    for face_landmarks in face_landmarks_list:

        for facial_feature in face_landmarks.keys():

            face_landmarks_max = [[int(j+2) for j in i]
                                for i in face_landmarks[facial_feature]]
            face_landmarks_max = [tuple(i) for i in face_landmarks_max]
            face_landmarks_min = [[int(j-2) for j in i]
                                for i in face_landmarks[facial_feature]]
            face_landmarks_min = [tuple(i) for i in face_landmarks_min]

            for i in range(len(face_landmarks_min)):
                d.ellipse(
                    (face_landmarks_min[i]+face_landmarks_max[i]), fill=GREEN, outline=None, width=stroke1)
            d.line(face_landmarks[facial_feature], fill=GREEN, width=stroke1)
    return result

def verify(imageName,originalImagePath,facial_landmarks):
    unknownEncoding = find_encoding(f'{VERIFY_IMAGE}/{imageName}')
    originalEncoding = find_encoding(originalImagePath[0])

    matches = face_recognition.compare_faces(originalEncoding, unknownEncoding[0], tolerance=MODEL_TOLERANCE)
    faceDis=face_recognition.face_distance(originalEncoding, unknownEncoding[0])
    matchIndex=np.argmin(faceDis)
    dist = faceDis[matchIndex]
    simScore = 1/math.exp(dist)
    if (dist>MODEL_TOLERANCE):
        simScore = simScore- 1/math.exp(1)
    simScore = simScore*100                   # converting to percentage 

    if (len(originalEncoding)>1 and matches[matchIndex]):
        encodedOriginalImage = get_from_multi_face(originalImagePath, matchIndex)
    else:
        encodedOriginalImage= utils.img_to_base64(originalImagePath[0]) 

    result={
    "similar": bool(matches[matchIndex]),
    "similarity_score": float(round(simScore, 2)),
    "original_image": encodedOriginalImage,
    "no_of_person": len(originalEncoding),
    "match_index": matchIndex + 1,
        }

    if facial_landmarks:
        img_landmarks=find_landmarks(f"{VERIFY_IMAGE}/{imageName}")
        img_landmarks.save(LANDMARK_IMAGE + imageName)
        encoded_landmark_image=utils.img_to_base64(LANDMARK_IMAGE + imageName)
        result["landmark_image"] = encoded_landmark_image
    return result


# TODO Rename this here and in `verify`
def get_from_multi_face(originalImagePath, matchIndex):
    imgFile = cv2.imread(originalImagePath[0])
    boundImg = cv2.cvtColor(imgFile,cv2.COLOR_BGR2RGB)
    faceCurFrame = face_recognition.face_locations(boundImg)
    y1,x2,y2,x1 = faceCurFrame[matchIndex]
    cv2.rectangle(boundImg,(x1,y1),(x2,y2),(255,0,0),2)
    _, buffer = cv2.imencode('.jpg', boundImg)
    return base64.b64encode(buffer)

def face_emotion(imagPath):
    image = cv2.imread(imagPath)
    img = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    faceCurFrame = face_recognition.face_locations(img)
    y1, x2, y2, x1 = faceCurFrame[0]
    # x_bound = int(0.05 * img.shape[0]) #increase crop boundary by 5%
    # y_bound = int(0.05 * img.shape[1])
    x_bound = 0
    y_bound = 0
    crop_img = image[y1-y_bound:y2+y_bound, x1-x_bound:x2+x_bound]
    gray = cv2.cvtColor(crop_img, cv2.COLOR_BGR2GRAY)
    resized_face = cv2.resize(gray, (64, 64))
    processed_face = resized_face.reshape(1, 1, 64, 64)
    net = cv2.dnn.readNetFromONNX(EMOTION_MODEL)
    net.setInput(processed_face)
    Output = net.forward()
    expanded = np.exp(Output - np.max(Output))
    probablities = expanded / expanded.sum()
    prob = np.squeeze(probablities)
    return emotions[prob.argmax()]

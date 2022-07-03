import base64
import shutil
import urllib.request
import os
import cv2


def grey_scale(file):
    img = cv2.imread(file)
    return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

def img_process(imgPath):
    gray = grey_scale(imgPath)
    return cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

def img_to_base64(imageFullPath):
    with open(imageFullPath, "rb") as img_file:
        encoded_image_string = base64.b64encode(img_file.read())
    return (encoded_image_string)


def save_image(image_path, image):
    with open(image_path, "wb") as buffer:
        shutil.copyfileobj(image, buffer)


def download_file(path: str, file_url: str, file_name: str):
    # add header agent as needed
    opener = urllib.request.build_opener()
    opener.addheaders = [
        ('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1941.0 Safari/537.36')]
    urllib.request.install_opener(opener)
    file_path = os.path.join(path, file_name)
    try:
        urllib.request.urlretrieve(file_url, file_path)
    except :
        return False
    else:
        return True

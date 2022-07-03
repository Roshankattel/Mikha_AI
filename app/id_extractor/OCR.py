import re
import PIL.Image as Image
import io
import pytesseract
from pytesseract import Output
from .. import utils
from ..mrz_reader.country_json import *
from passporteye import read_mrz
from ..config import settings


def clean_name(name):
    pattern = re.compile('([^\s\w]|_\<)+')
    name = pattern.sub('', name)
    return name.strip()

def mrz_parser(file):

    # print(file)
    pil_im = Image.fromarray(file)
    b = io.BytesIO()
    pil_im.save(b, 'jpeg')
    im_bytes = b.getvalue()

    # Process image
    mrz = read_mrz(im_bytes)

    if mrz is None:
        return print("Can not read image")

    mrz_data = mrz.to_dict()

    user_info = {'last_name': mrz_data.get('surname').upper()}
    user_info['first_name'] = clean_name(mrz_data.get('names').upper())
    user_info['country_code'] = mrz_data.get('country')
    user_info['country'] = get_country_name(user_info.get('country_code'))
    user_info['nationality'] = get_country_name(mrz_data.get('nationality'))
    user_info['number'] = clean_name(mrz_data.get('number'))
    user_info['sex'] = mrz_data.get('sex')
    # user_info['valid_score'] = mrz_data.get('valid_score')
    return user_info


def extract_feilds(dict,txt):
  # index 
  nameIndex,dobIndex,idIndex=0,0,0

  #extract feilds
  name ,dob ,idNo = "","",""

  #Confidence values
  nameConf,dobConf,idConf = 0,0,0

  #clear data - A-Z,a-z and 0-9
  for index,i in enumerate(dict["text"]):
    dict["text"][index] = re.sub(r"[^a-zA-Z0 -9]","",i)

  # print ( dict["text"])
  #find indexs of name,dob and id

  for index,word in enumerate(dict["text"]):
    if(word.upper() =="NAME"):
      nameIndex = index+1
    if word.upper() in ["BIRTH", "OFBIRTH"]:
      dobIndex = index+1
    if word.upper() in ["NO", "IDNO"]:
      idIndex = index+1

  if(nameIndex!=0):
    if (dict["conf"][nameIndex+2]=="-1"):
      name = dict["text"][nameIndex] + " "+ dict["text"][nameIndex+1]
      nameConf = round((float(dict["conf"][nameIndex]) + float(dict["conf"][nameIndex+1]))/2)
    else:
      name = dict["text"][nameIndex] + " "+ dict["text"][nameIndex+1]+" "+ dict["text"][nameIndex+2]
      nameConf = round((float(dict["conf"][nameIndex]) + float(dict["conf"][nameIndex+1])+ float(dict["conf"][nameIndex+2]))/3)

  if(dobIndex!=0):
    dob = dict["text"][dobIndex] + " "+ dict["text"][dobIndex+1]+" "+ dict["text"][dobIndex+2]
    dobConf = round((float(dict["conf"][dobIndex]) + float(dict["conf"][dobIndex+1])+float(dict["conf"][dobIndex+2]))/3)


  if(idIndex!=0):
    if ((idIndex+1)==len(dict["conf"])or dict["conf"][idIndex+1]=="-1"):
      idNo = dict["text"][idIndex] 
      idConf = round(float(dict["conf"][idIndex]))
    else:
      idNo = dict["text"][idIndex] + dict["text"][idIndex+1]
      idConf = round((float(dict["conf"][idIndex])+ float( dict["conf"][idIndex+1]))/2)

  if (nameConf==0):
    txtName = re.search("Name:[\w\s,.]+", txt)
    if txtName:
      name = _extracted_from_extract_feilds_50(txtName)
  if (idConf==0):
    txtNid = re.search("ID NO:[ \d \"\[.+\]\" ' ]+", txt)
    if txtNid:
      txtNid = txtNid[0]
      txtNid = re.findall(r'\d+', txtNid)
      txtNid = ''.join(txtNid)
      idNo = txtNid

  if (dobConf==0):
    txtDob = re.search("Date of Birth:[ \w\s,.]+", txt)
    if txtDob :
      dob = _extracted_from_extract_feilds_50(txtDob)
  return (name,nameConf,dob,dobConf,idNo,idConf)


# TODO Rename this here and in `extract_feilds`
def _extracted_from_extract_feilds_50(arg0):
  arg0 = arg0[0].split(":")
  arg0 = arg0[1].strip()
  arg0 = arg0.split("\n")[0]
  return arg0

def process_id_extract(imagePath:str,raw_data:bool,feilds:bool,lanaguage = "eng"):
  result = {}
  procesImg=utils.img_process(imagePath)
  extractDict = pytesseract.image_to_data(procesImg, output_type=Output.DICT)
  extractTxt = pytesseract.image_to_string(procesImg, lang=lanaguage)
  # print(extractTxt)
  if feilds:
    result = _extracted_from_process_id_extract_8(extractDict, extractTxt)
  if raw_data:
    result["extract_data"] = extractTxt
  return result


# TODO Rename this here and in `process_id_extract`
def _extracted_from_process_id_extract_8(extractDict, extractTxt):
  name, nameConf,dob,dobConf,idNo,idConf = extract_feilds(extractDict,extractTxt)
  # print(extractTxt)

  feildName = {"data":name,"confidence":nameConf}
  feildDob = {"data":dob,"confidence":dobConf}
  feildID = {"data":idNo,"confidence":idConf}
  return {"name":feildName,"dob":feildDob,"id_no":feildID}

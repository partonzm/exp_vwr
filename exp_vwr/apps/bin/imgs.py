import base64, io
import numpy
from PIL import Image

def byt_out(jpg):
    with open(jpg, "rb") as imageFile:
        return(base64.b64encode(imageFile.read()))


def img_out(st):
    return(Image.open(io.BytesIO(base64.b64decode(st))))

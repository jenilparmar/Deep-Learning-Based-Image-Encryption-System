import hashlib
import numpy as np
from PIL import Image
def img_SHA_512(relative_path):
    img = Image.open(rf"{relative_path}")
    img_array = np.array(img)
    flat_arr = img_array.flatten()
    text = "".join(str(item) for item in flat_arr)
    hash_object = hashlib.sha512(text.encode())
    hash_hex = hash_object.hexdigest()
    return hash_hex


def create_sha_key(a):
    hash_object = hashlib.sha512(a.encode())
    hash_hex = hash_object.hexdigest()
    return hash_hex

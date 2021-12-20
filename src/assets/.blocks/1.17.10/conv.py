"""make json file out of block pixels"""

import os
from PIL import Image
import json
def main():
    path = "original/"
    dictionary = {
        "version": "1.17.10",
        "data": []
    }
    for f in os.listdir(path):
        if os.path.isfile(path + f):
            newsize = (1,1)
            image = Image.open(path + f).convert("RGB")
            pxl_image = image.resize(newsize, resample=Image.ANTIALIAS)
            pxl_image.save("1px/" + f)
            r, g, b = pxl_image.getpixel((0,0))
            
            dictionary["data"].append(
                {
                    "block": f[0:-4],
                    "rgb": [r, g, b],
                    "enabled": True
                }
            )
    with open("values.json", "w") as file:
        data = json.dumps(dictionary, indent=4)
        file.write(data)


if __name__ == '__main__':
    main()

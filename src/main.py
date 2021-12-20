#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Create a Pixel Art in Minecraft Bedrock Edition.

The full documentation can be found in the documentation
folder. Notice that by importing this module it will raise
an error. Its purpose is to be executed as main.
"""

#############################################
# ABOUT #####################################

__version__ = "0.0.1a0"
__author__ = "phoenixR"
__maintainer__ = ""
__copyright__ = "Copyright 2021, The-phoenixR"
__license__ = "MIT"
__status__ = "Development"
__credits__ = []


#############################################
# INFO ######################################

"""
[ INFO ]
* This project is archived and won't be developed
* anymore.
* 
* In case you use the colors.json file
* I would appreciate if you credit me
* because there is no way of automating
* it so I had to rename every file into
* the corresponding block name + id.

[ TODO ]
* when executing place function it gives a tag (e.g. pa.place.a)
* if ( tag == pa.place.a ) => run function a_0
* if ( tag == pa.place.a ) => get tag pa.a.temp.a_0
* if ( tag == pa.place.a ) => run function a_1
* if ( tag == pa.place.a ) => get tag pa.a.temp.a_1
* ...
* Light Version for under 10000b2 field
* if (tag == pa.place.a, pa.a.temp... ) => remove this.tags
* change Pixelart" to "Pixel Art"
* notice overwrite option
* check which characters work
* if imsize > finalsize => 
* add additional htm with Projects
* sort used_blocks amount
* add mc version from toml manifest due to using blocks
* minimize pa size so its function amount is not above 10k
"""

#############################################
# CODE ######################################

if __name__ != "__main__":
    raise BaseException("Script not executable on import!")

# imports
## built-in
import colorsys
import importlib
import json
import math
import os
import re
import shutil
import string
import sys
from datetime import datetime
from distutils.dir_util import copy_tree
import uuid

## third party
#os.system("pip install -r assets/.requirements.txt")
from PIL import Image
import toml
from unidecode import unidecode

## local
with open(".include","r") as f:
    MODULE = {}
    for line in f.readlines():
        head, tail = os.path.split(line)
        tail = os.path.splitext(tail)
        sys.path.append(head)
        MODULE[tail] = importlib.import_module(tail)


DEBUG = True

answer = input("Press [Enter] to start")
if answer == "RESET":
    print("resetting assets ...")
    MODULE["reset_assets"].reset()
    exit()


# load data
path = "assets/config/"
## config.toml
with open(path + "config.toml", "r") as f:
    Config = toml.loads(f.read())
    Direction = Config["pixelart"]["create-mode"]["mode"]
    Placeholder = "" if Config["pixelart"]["replace"]["block"] == "" else Config["pixelart"]["replace"]["block"]
    BPFolderName = Config["pack"]["folder_name"]
    PackName = Config["pack"]["name"]
    PackDescription = Config["pack"]["description"]
    Minecraft_version = Config["meta"]["minecraft_version"].split(".")

## colors.json
with open(path + "colors.json", "r") as f:
    Colors_original = json.loads(f.read())
    Colors = {"data":[]}
    for color in Colors_original["data"]:
        if color["enabled"]:
            Colors["data"].append(color)

## commands
class Commands:
    tellraw = "tellraw @s {\"rawtext\":[{\"text\":\"%s\"}]}"
    function = "function pa/place/sub/%s/%d"
    setblock = "setblock ~{x} ~{y} ~{z} {block}"
    info = "§l§6Pixelart Info§r\\n§c===§6===§e===§a===§b===§9===§r\\n§5Used blocks:\\n"
    info_format = "  {block}: {amount}\\n"

## profanity list
with open(path + ".profanity.txt", "r") as f:
    Profanity = f.readlines()

## manifest
path = "assets/.default#behavior_pack/Pixelart/"
with open(path + "manifest.json", "r") as f:
    Manifest = json.loads(f.read())

## cache
Cache = {}
with open("assets/.cache/cache", "r") as f:
    comment = "::"
    for l in f.readlines():
        p = rf"^\s*{comment}"
        if re.match(p, l):
            continue
        l = l.split(comment, 1)[0]
        Cache[l.split("=", 1)[0]] = l.split("=", 1)[1]


# main
legalchars = list(string.ascii_letters + string.digits) + ["_", "-", ";", "#", "$"]

def log(*text):
    result = []
    for i in text:
        result.append(str(i))
    return " ".join(result)

def to_zip(src, dst):
    shutil.make_archive(dst.rsplit(".", 1)[0], "zip", src)
    shutil.move(dst.remove(".zip"), dst)

def closest_color(r, g, b):
    color_diffs = []
    for color in Colors["data"]:
        cr, cg, cb = color["rgb"]
        color_diff = math.sqrt(
            abs(r - cr)**2 +
            abs(g - cg)**2 +
            abs(b - cb)**2
        )
        color_diffs.append((color_diff, color["block"]))
    return min(color_diffs)[1]


srcpath = path
dstpath = "assets/behavior_pack/" + BPFolderName
try:
    shutil.rmtree(dstpath)
except FileNotFoundError:
    pass
os.mkdir(dstpath)
copy_tree(srcpath, dstpath)
srcpath = "assets/config/pack_icon.png"
dstpath = "assets/behavior_pack/" + BPFolderName +"/pack_icon.png"
shutil.copyfile(srcpath, dstpath)


path = "assets/behavior_pack/" + BPFolderName + "/functions/pa/place/"
for d in Direction:
    os.mkdir(path + d)

mbfactor = 1000000
continue_ = True
fsize = 0
path = "assets/images/"
for file in os.listdir(path):
    print(file)
    if fsize > mbfactor:
        continue_ = False
        while True:
            answer = input(f"Warning: This Behavior Pack takes up 10 MB ({round(fsize / mbfactor)} MB). Are you sure you want to continue? (y/N) [y]")
            if answer.lower() in ["y", ""]:
                continue_ = True
                break
            elif answer.lower() == "n":
                break
    if continue_:
        used_blocks = {}
        for block in Colors["data"]:
            used_blocks[block["block"]] = 0
        path = "assets/images/"
        if os.path.isfile(path + file) and file.lower()[-1] in [".png", ".jpg", ".jpeg", ".bmp", ".blockdata"]:
            image = Image.open(path + file).convert("RGBA").transpose(Image.FLIP_TOP_BOTTOM)
            image_size = image.size
            function_name = []
            for l in file.rsplit(".", 1)[0]:
                if l in legalchars:
                    function_name.append(l)
                else:
                    function_name.append("_")
            function_name = unidecode("".join(function_name))
            for w in Profanity:
                function_name = function_name.replace(w, "x"*len(w))
            newsize = {}
            length = Config["pixelart"]["size"]["via"].lower()
            value = Config["pixelart"]["size"]["value"]
            newsize[length] = value
            if length == "w":
                factor = image_size[0] / value
                newsize["h"] = int(image_size[1] // factor)
            elif length == "h":
                factor = image_size[1] / value
                newsize["w"] = int(image_size[0] // factor)
            pxl_image = image.resize(
                (newsize["w"], newsize["h"]),
                resample = Image.ANTIALIAS
            )
            pixels = pxl_image.width * pxl_image.height
            func_path = "assets/behavior_pack/" + BPFolderName + "/functions/pa/place/"
            c = 0 # counter 1
            d = 0 # counter 2
            for w in range(pxl_image.width):
                for h in range(pxl_image.height):
                    cr, cg, cb, ca = pxl_image.getpixel((w, h))
                    ch, cs, cv = colorsys.rgb_to_hsv(cr, cg, cb)
                    if Config["pixelart"]["chroma-key"]["active"] and MODULE["chromakey"].ChromaKey((ch, cs, cv)).color() == Config["pixelart"]["chroma-key"]["color"]:
                        block = Placeholder
                    elif ca < Config["pixelart"]["alpha-replace"]["alpha_value"]:
                        block = Placeholder
                    else:
                        block = closest_color(cr, cg, cb)
                    if block != "":
                        used_blocks[block] += 1
                        if "h" in Direction:
                            if d % 10000 == 0:
                                fh = open(func_path + "sub/h/" + function_name + "_" + str(c) + ".mcfunction", "w")
                            fh.write(Commands.setblock.format(x=w, y=-1, z=h, block=block) + "\n")
                        if "v" in Direction:
                            if d % 10000 == 0:
                                fv = open(func_path + "sub/v/" + function_name + "_" + str(c) + ".mcfunction", "w")
                            fv.write(Commands.setblock.format(x=w, y=h, z=0, block=block) + "\n")
                        if d % 10000 == 0:
                            c += 1
                        d += 1
            str_used_blocks = json.dumps(used_blocks, indent=4, sort_keys=True)
            try:
                fh.close()
            except NameError:
                pass
            try:
                fv.close()
            except NameError:
                pass
            for d in Direction:
                with open("assets/behavior_pack/" + BPFolderName + "/functions/pa/place/" + d + "/" + function_name + ".mcfunction", "w") as f:
                    commands = []
                    for i in range(c):
                        commands.append("function pa/place/sub/" + d + "/" + function_name + "_" + str(i))
                    f.write("\n".join(commands))
                with open("assets/behavior_pack/" + BPFolderName + "/functions/pa/used_blocks/" + function_name + ".mcfunction", "w") as f:
                    result = Commands.info
                    for key in used_blocks:
                        value = used_blocks[key]
                        result += Commands.info_format.format(block = key, amount = str(value))
                    f.write(Commands.tellraw % result)
            path = "assets/behavior_pack/" + BPFolderName + "/manifest.json"
            with open(path, "r") as f:
                this_manifest = json.loads(f.read())
                if Config["pixelart"]["update"]["active"] and Cache["made_pack"]:
                    version = this_manifest["header"]["version"]
                    version[-1] += 1
                    this_manifest["header"]["version"] = version
                    version = this_manifest["modules"][0]["version"]
                    version[-1] += 1
                else:
                    this_manifest["header"]["name"] = PackName + (datetime.now().strftime(" [%H:%M]") if DEBUG else "")
                    this_manifest["header"]["description"] = PackDescription
                    this_manifest["header"]["uuid"] = str(uuid.uuid4())
                    this_manifest["header"]["min_engine_version"] = Minecraft_version
                    this_manifest["modules"][0]["description"] = PackDescription
                    this_manifest["modules"][0]["uuid"] = str(uuid.uuid4())
                Cache["made_pack"] = 1
            with open(path, "w") as f:
                f.write(json.dumps(this_manifest, indent=4))
            #if Config["pack"]["folder_type"] in ["zip", "mcpack"]
        else:
            print(file + " has not a correct file format. Take a look at")


# make cache
'''
for key, value in Cache:
   with open("assets/.cache/cache", "r+") as f:
       pass
'''

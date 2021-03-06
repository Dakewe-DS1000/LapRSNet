import os, time, random
import numpy as np
import scipy

import tensorflow as tf
import tensorlayer as tl
from model import *
from utils import *
from config import *
import cv2
import math
import pdb #用于debug跟踪调试

oriImageName = "samples/test/test_origin.bmp"
resImageName = "samples/test/test_out.bmp"

if __name__ == '__main__':
    # Load origin image and result output image
    origin_image = cv2.imread(oriImageName, 0)
    result_image = cv2.imread(resImageName, 0)

    if origin_image.shape == 3 :
        raise Exception("Please Read image as Gray Scale")
    if result_image.shape == 3 :
        raise Exception("Please Read image as Gray Scale")

    oriHeight, oriWidth = origin_image.shape
    resHeight, resWidth = result_image.shape

    if oriWidth!=resWidth:
        raise Exception("Size of Origin Image and Result Image is Different")
    if oriHeight != resHeight :
        raise Exception("Size of Origin Image and Result Image is Different")

    print("origin image size : (", oriWidth, " , ", oriHeight, ")")
    print("result image size : (", resWidth, " , ", resHeight, ")")

    diff = 0.0
    for y in range(oriHeight) :
        for x in range(oriWidth) :
            diff += (float(origin_image[y, x]) - float(result_image[y, x])) * (float(origin_image[y, x]) - float(result_image[y, x]))

    diff /= oriHeight * oriWidth
    print("DIFF : ", diff)

    rmse = math.sqrt(diff)
    print("RMSE : ", rmse)

    psnr = 20.0 * math.log10(255.0 / rmse)
    print("PSNR : ", psnr, " [dB]")
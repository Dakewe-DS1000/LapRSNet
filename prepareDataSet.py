# Prepare my dataset for Digital Pathology

import os
import math
import cv2

import pdb

rootFolder = "F:\DataBase\LymphnodePathology"
trainFolder = rootFolder + "\\trainDataSet"
testFolder = rootFolder + "\\testDataSet"

srcTrainFilePath = trainFolder + "\\20X\\"
dstTrainFilePath = trainFolder + "\\5X\\"
srcTestFilePath  = testFolder  + "\\20X\\"
dstTestFilePath  = testFolder  + "\\5X\\"

factor = 4

if __name__ == '__main__':
    srcTrainFileNameList = os.listdir(srcTrainFilePath)
    srcTestFileNameList  = os.listdir(srcTestFilePath)

    for srcTrainFileName in srcTrainFileNameList:
        srcTrainImage = cv2.imread(srcTrainFilePath + srcTrainFileName)

        imgHeight, imgWidth, _ = srcTrainImage.shape
        newWidth = int(imgWidth / factor)
        newHeight = int(imgHeight / factor)
        newSize = (newWidth, newHeight)

        dstTrainImage = cv2.resize(srcTrainImage, newSize, interpolation=cv2.INTER_AREA)

        print("Train File Name : %s, (%d, %d) => (%d, %d)" %(srcTrainFileName, imgWidth, imgHeight, newSize[0], newSize[1]))
        cv2.imwrite(dstTrainFilePath + srcTrainFileName, dstTrainImage)

    for srcTestFileName in srcTestFileNameList:
        srcTestImage = cv2.imread(srcTestFilePath + srcTestFileName)

        imgHeight, imgWidth, _ = srcTestImage.shape
        newWidth = int(imgWidth / factor)
        newHeight = int(imgHeight / factor)
        newSize = (newWidth, newHeight)

        dstTestImage = cv2.resize(srcTestImage, newSize, interpolation=cv2.INTER_AREA)

        print("Test File Name : %s, (%d, %d) => (%d, %d)" %(srcTestFileName, imgWidth, imgHeight, newSize[0], newSize[1]))
        cv2.imwrite(dstTestFilePath + srcTestFileName, dstTestImage)

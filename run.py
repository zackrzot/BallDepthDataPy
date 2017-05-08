import os
import numpy
from PIL import Image, ImageDraw
import cv2
import math
import matplotlib.pyplot as plt
import datetime

fullDatPath = "full/dat/"
fullImgPath = "full/img/"
ballPath = "ball/"

maxDepth = 3100
minDepth = 1500
threshold = .9999
ballDim = 35
ballOverlap = 10


startX = 120
endX = 310
maxSliceDepth = 200


# takes into account the extra tab and new line in data files
def getDim(text):
    return ((len(text.split('\n'))-1), (len(text.split('\n')[0].split('\t'))-1))
# =============================================================== #
def getArrayFromText(text, m, n):
    arr = numpy.zeros((m,n))
    r = 0
    rows = text.split('\n')
    for row in rows:
        c = 0
        cols = row.split('\t')
        for col in cols:
            col = col.strip()
            if(col == ""):
                break
            col = int(col)
            if col == 0:
                col = maxDepth
            if col > maxDepth:
                col = maxDepth
            if col < minDepth:
                col = minDepth
            arr[r, c] = col
            c+=1
        r+=1
    return arr
# =============================================================== #
def getArrayFromFile(filePathAndName):
    # load raw string data
    text = ""
    with open(filePathAndName, 'r') as f:
        text = f.read()
    # get width and height from string data
    m, n = getDim(text)
    #print "rows (m) = " + str(m)
    #print "cols (n) = " + str(n)
    # parse text data and generate array
    arr = getArrayFromText(text, m, n)
    #print arr
    return arr
# =============================================================== #
def getShade(minVal, maxVal, val):
    a = maxVal - minVal
    b = val - minVal
    if b == 0:
        return 0
    c = b / a
    x = (int) (255-(math.ceil(c*255)))
    return x
# =============================================================== #
def getImage(arr):
    minVal = arr.min()
    maxVal = arr.max()
    img = Image.new('RGB', (arr.shape[1], arr.shape[0]), "black")
    pmap = img.load()

    maxVal = minVal + maxSliceDepth

    for row in range(arr.shape[0]):
        for col in range(arr.shape[1]):
            cellVal = arr[row,col]
            if cellVal > maxVal:
                cellVal = maxVal
            s = getShade(minVal,maxVal,cellVal)
            pmap[col,row] = (s,s,s)
    return img
# =============================================================== #
def templateMatch(fullImage, templateFile, inList):
    # Template File
    #print templateFile
    template = cv2.imread(templateFile, 1)
    template = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
    res = cv2.matchTemplate(fullImage, template, cv2.TM_CCORR_NORMED)

    w, h = template.shape[::-1]
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    top_left = min_loc
    bottom_right = (top_left[0] + w, top_left[1] + h)

    loc = numpy.where( res >= threshold)
    for pt in zip(*loc[::-1]):
        if isOverlap(inList, pt, w, h) == False:
            inList.append(pt)

    return inList
# =============================================================== #
def isOverlap(inList, pt, w, h):
    for item in inList:
        if (abs(pt[0] - item[0]) <= ballOverlap) and (abs(pt[1] - item[1]) <= ballOverlap):
            return True
    return False
# =============================================================== #
def genImages(datPath, imgPath):
    for filename in os.listdir(datPath):
        arr = getArrayFromFile(datPath+filename)
        # generate image from arr
        img = getImage(arr)
        img.save(imgPath + filename.replace(".txt", ".png"))
# =============================================================== #
def getGradient(datFile):
    arrFull = getArrayFromFile(fullDatPath+datFile)
    img = getImage(arrFull)
    return img
# =============================================================== #
def findBalls(img, ballPath):
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    ballList = []
    for filename in os.listdir(ballPath):
        ballList = templateMatch(img, ballPath+filename, ballList)
    return ballList
# =============================================================== #
def drawBoxes(ballList, img):
    for item in ballList:
        cv2.rectangle(img, item, (item[0] + ballDim, item[1] + ballDim), (0,0,255), 1)
    return img
# =============================================================== #
def methodTemplateMatching():
    #genImages(fullDatPath, fullImgPath)

    a = datetime.datetime.now()

    datFile = "13b565f3-0062-4840-b75f-87a62423ca76_FULL.txt"
    datFile = "509e4984-7917-4722-8503-220efc0669bc_FULL.txt"
    datFile = "b0aa273e-716a-46c6-bb48-5b038965a132_FULL.txt"
    datFile = "de9ec5aa-6b6e-4941-ad7e-b8efcc94464e_FULL.txt"

    img = getGradient(datFile)

    # format image
    img = numpy.array(img) 
    img = img[:, :, ::-1].copy() 

    ballList = findBalls(img, ballPath)

    b = datetime.datetime.now()
    print "Calculation time: " + str(b-a)

    print ballList
    img = drawBoxes(ballList, img)

    cv2.imwrite("result/img.png", img)
# =============================================================== #

# Slicing
datFile = "13b565f3-0062-4840-b75f-87a62423ca76_FULL.txt"
datFile = "509e4984-7917-4722-8503-220efc0669bc_FULL.txt"
#datFile = "b0aa273e-716a-46c6-bb48-5b038965a132_FULL.txt"
#datFile = "de9ec5aa-6b6e-4941-ad7e-b8efcc94464e_FULL.txt"

arrFull = getArrayFromFile(fullDatPath+datFile)

sliceHeight = 15
x = startX
while x < arrFull.shape[0]-sliceHeight and x < endX:
    img = getImage(arrFull[x:x+sliceHeight])
    # format image
    img = numpy.array(img) 
    img = img[:, :, ::-1].copy() 
    cv2.imwrite("slices/"+str(x)+".png", img)
    x+=sliceHeight-5
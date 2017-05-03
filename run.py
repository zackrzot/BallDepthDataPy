import os
import numpy
from PIL import Image
import cv2

fullDatPath = "full/dat/"
sampleDatPath = "sample/dat/"
fullImgPath = "full/img/"
sampleImgPath = "sample/img/"
ballPath = "ball/"

# takes into account the extra tab and new line in data files
def getDim(text):
    return ((len(text.split('\n'))-1), (len(text.split('\n')[0].split('\t'))-1))

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
            arr[r, c] = col
            c+=1
        r+=1
    return arr

def getArrayFromFile(filePathAndName):
    # load raw string data
    text = ""
    with open(filePathAndName, 'r') as f:
        text = f.read()
    # get width and height from string data
    m, n = getDim(text)
    print "rows (m) = " + str(m)
    print "cols (n) = " + str(n)
    # parse text data and generate array
    arr = getArrayFromText(text, m, n)
    print arr
    return arr


def getShade(minVal, maxVal, val):
    if(minVal<0):
        minVal = 0
    x = 255-(int)((val/(maxVal-minVal))*255)
    return x

def getImage(arr):
    minVal = arr.min()
    maxVal = arr.max()
    #print "min: " + str(minVal)
    #print "max: " + str(maxVal)
    img = Image.new('RGB', (arr.shape[1], arr.shape[0]), "black")
    pmap = img.load()
    for row in range(arr.shape[0]):
        for col in range(arr.shape[1]):
            s = getShade(minVal,maxVal,arr[row,col])
            pmap[col,row] = (s,s,s)

    return img

def rebase(arr):
    minVal = arr.min()
    for row in range(arr.shape[0]):
        for col in range(arr.shape[1]):
            arr[row,col] = arr[row,col] - minVal
    return arr

def templateMatch(image):
    open_cv_image = numpy.array(image) 
    open_cv_image = open_cv_image[:, :, ::-1].copy() 
    open_cv_image = cv2.cvtColor(open_cv_image, cv2.COLOR_BGR2GRAY)
    highest = 0
    for file in os.listdir(ballPath):
        img2 = cv2.imread(ballPath+file, 1)
        img2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
        res = cv2.matchTemplate(img2, open_cv_image, cv2.TM_CCORR_NORMED)
        maxConf = numpy.max(res)
        if maxConf > highest:
            highest = maxConf
    return highest


# =============================================================== #
def genImages(datPath, imgPath):
    for filename in os.listdir(datPath):
        arr = getArrayFromFile(datPath+filename)
        # generate image from arr
        img = getImage(arr)
        img.save(imgPath + filename.replace(".txt", ".png"))
# =============================================================== #
def matchTempate(datFile, sampleFile):
    print "Full Data"
    arrFull = getArrayFromFile(fullDatPath+datFile)
    print "Sample Data"
    arrSample = getArrayFromFile(sampleDatPath+sampleFile)

    originX = 0
    originY = 0
    sampleW = arrSample.shape[0]
    sampleH = arrSample.shape[1]
    maxSearchX = arrFull.shape[0]-sampleW
    maxSearchY = arrFull.shape[1]-sampleH

    count = 0

    maxconf = 0
    minconf = 9999
    thresh = .80
    threshCount = 0
    slide = 5


    points = []

    while originX <= maxSearchX:
        print str(originX)+"/"+str(maxSearchX)
        originY = 0
        while originY <= maxSearchY:
            # get sample of same size from full image
            arrSub = arrFull[originX:originX+sampleW, originY:originY+sampleH]
            # rebase to 0
            #arrSub = rebase(arrSub)
            # 
            img = getImage(arrSub)
            #img.save("result/" + str(count)+ ".png")
            conf = templateMatch(img)

            if conf > maxconf:
                maxconf = conf
            if conf < minconf:
                minconf = conf
            if conf > thresh:
                threshCount+=1
                img.save("result/" + str(count)+ ".png")


            originY+=slide
            count+=1
        originX+=slide

    #img = getImage(arrFull)
    #img.save("result/" + datFile.replace(".txt", ".png"))

    print "searches conducted = " + str(count)
    print "maxconf = " + str(maxconf)
    print "minconf = " + str(minconf)
    print "threshCount = " + str(threshCount)



# =============================================================== #


#genImages(fullDatPath, fullImgPath)
#genImages(sampleDatPath, sampleImgPath)

datFile = "13b565f3-0062-4840-b75f-87a62423ca76.txt_FULL.txt"
sampleFile = "9ff3e1f8-aa4a-40bc-857b-640e54c5d982.txt"
matchTempate(datFile,sampleFile)


import numpy as np
import cv2
import colorsys
import collections
import sys
import time
import cassandra
from cassandra.cluster import Cluster

# Building Blocks

class Position(object):
    def __init__(self, _x, _y, _w, _h):
        self.x = _x
        self.y = _y
        self.w = _w
        self.h = _h

    def x(self):
        return self.x

    def y(self):
        return self.y

    def w(self):
        return self.w

    def h(self):
        return self.h


class People(object):
    def __init__(self, _x, _y, _w, _h, _roi, _hue):
        # Position
        self.x = _x
        self.y = _y
        self.w = _w
        self.h = _h
        self.roi = _roi

        # Display of the contour while tracking
        self.hue = _hue
        self.color = hsv2rgb(self.hue % 1, 1, 1)

        # Motion Descriptors
        self.center = [_x + _w / 2, _y + _h / 2]
        self.isIn = checkPosition(boundaryPt1, boundaryPt2, self.center, inCriterion)
        self.isInChangeFrameCount = toleranceCountIOStatus
        self.speed = [0, 0]
        self.missingCount = 0

        # ROI - Region of Interest
        self.maxRoi = _roi
        self.roi = _roi

    def x(self):
        return self.x

    def y(self):
        return self.y

    def w(self):
        return self.w

    def h(self):
        return self.h

    def roi(self):
        return self.roi

    def color(self):
        return self.color

    def center(self):
        return self.center

    def maxRoi(self):
        return self.maxRoi

    def isIn(self):
        return self.isIn

    def speed(self):
        return self.speed

    def missingCount(self):
        return self.missingCount

    def isInChangeFrameCount(self):
        return self.isInChangeFrameCount

    def set(self, name, value):
        if name == "x":
            self.x = value
        elif name == "y":
            self.y = value
        elif name == "w":
            self.w = value
        elif name == "h":
            self.h = value
        elif name == "center":
            self.center = value
        elif name == "roi":
            self.roi = value
            # Automatically update maxRoi as roi is updated
            if self.roi.shape[0] * self.roi.shape[1] > self.maxRoi.shape[0] * self.maxRoi.shape[1]:
                self.maxRoi = self.roi
        elif name == "speed":
            self.speed = value
        elif name == "missingCount":
            self.missingCount = value
        elif name == "isIn":
            self.isIn = value
        elif name == "isInChangeFrameCount":
            self.isInChangeFrameCount = value
        else:
            return


# Functionality

def averageSize():
    sum = 0
    for i in humanSizeSample:
        sum += i
    return sum / sampleSize


# Top and Bottom considered

def checkTouchVSide(x, y, w, h, maxW, maxH, tolerance):
    if x <= 0:
        return True
    elif y - tolerance <= 0:
        return True
    elif x + w >= maxW:
        return True
    elif y + h + tolerance >= maxH:
        return True
    else:
        return False

# Defining Exterior Bounding Box

def getExteriorRect(pts):
    xArray = []
    yArray = []
    for pt in pts:
        xArray.append(pt[0])
        yArray.append(pt[1])
    xArray = sorted(xArray)
    yArray = sorted(yArray)
    return (xArray[0], yArray[0], xArray[3] - xArray[0], yArray[3] - yArray[0])


# Extracting Color

def hsv2rgb(h, s, v):
    return tuple(i * 255 for i in colorsys.hsv_to_rgb(h, s, v))


# Checking and Re-affirming the location

def checkPosition(boundaryPt1, boundaryPt2, currPos, inCriterion):
    m = (boundaryPt2[1] - boundaryPt1[1]) / (boundaryPt2[0] - boundaryPt1[0])
    c = boundaryPt2[1] - m * boundaryPt2[0]
    if inCriterion == "<":
        if currPos[0] * m + c < currPos[1]:
            return True
        else:
            return False
    elif inCriterion == ">":
        if currPos[0] * m + c > currPos[1]:
            return True
        else:
            return False
    else:
        return False

def getAnswer(str):
    return str


def nothing(x):
    pass





# Sourcing the video

srcTest = 'publicDensity.avi'
srcWebcam = 0
srcMain = ''  # we can also use a live source here
cap = cv2.VideoCapture(srcTest)  # Open video file

# Configuring and Pre-Processing Data

minArea = 500  # default min area to be considered person
maxArea = 4000  # default max area to be considered person
noFrameToCollectSample = 100
toleranceRange = 50  # use for error calculation
toleranceCount = 10  # maximum number of frame an object need to present in order to be accepted
toleranceCountIOStatus = 3  # minimum number of frame between In/Out Status change -> prevent playing with the system
startHue = 0  # In HSV this is RED
hueIncrementValue = 0.1  # increment color every time to differentiate between different people

# Creating Setup

fgbg = cv2.createBackgroundSubtractorMOG2(detectShadows=True)
sampleSize = 100
humanSizeSample = collections.deque(maxlen=sampleSize)

midHeight = int(cap.get(4) / 2)
maxWidth = cap.get(3)
maxHeight = cap.get(4)

inCriterion = "<"
boundaryPt1 = [0, midHeight - 100]
boundaryPt2 = [maxWidth, midHeight]

# This is where we track

# Passage Control
allowPassage = True
peopleViolationIn = 0
peopleViolationOut = 0
switch = '0 : PASS \n1 : STOP'

# Initializa Other Variable
averageArea = 0.000  # for calculation of min/max size for contour detected
peopleIn = 0  # number of people going up
peopleOut = 0  # number of people going up
frameCounter = 0
maskT = None
passImage = None
detectedPeople = []
detectedContours = []

frame_no = int(400)
count = 0


# take first frame of the video
_, pFrame = cap.read()

# Tracking the number of frames
cluster = Cluster()
session = cluster.connect('densely')
count = 0

while (count < frame_no):
    count += 1


    # RE-Initialize
    frameInfo = np.zeros((400, 500, 3), np.uint8)
    averageArea = averageSize()
    ret, frame = cap.read()  # read a frame
    if (frame is not None):
        frameForView = frame.copy()
    else:
        break



    # Clean Frame
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    fgmask = fgbg.apply(gray)
    blur = cv2.medianBlur(fgmask, 5)
    thresh = cv2.threshold(blur, 127, 255, cv2.THRESH_BINARY)[1]  # shadow of MOG@ is grey = 127
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    closing = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)  # fill any small holes
    opening = cv2.morphologyEx(closing, cv2.MORPH_OPEN, kernel)  # remove noise
    contours = cv2.findContours(opening.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[1]

    mask_opening = cv2.inRange(opening, np.array([0]), np.array([128]))
    noBg = cv2.bitwise_and(frame, frame, mask=mask_opening)

    # Process Contours
    for c in contours:
        # Filter Contour By Size
        if len(humanSizeSample) < 100:
            if cv2.contourArea(c) < minArea or cv2.contourArea(c) > maxArea:
                continue
            else:
                humanSizeSample.append(cv2.contourArea(c))
        else:
            if cv2.contourArea(c) < averageArea / 2 or cv2.contourArea(c) > averageArea * 3:
                continue
        (x, y, w, h) = cv2.boundingRect(c)
        detectedContours.append(Position(x, y, w, h))

    # Process Detected People
    if len(detectedPeople) != 0:
        for people in detectedPeople:

            # Setup Meanshift/Camshift for Tracking
            track_window = (int(people.x), int(people.y), int(people.w), int(people.h))
            hsv_roi = pOpening[int(people.y):int(people.y) + int(people.h), int(people.x):int(people.x) + int(people.w)]
            mask = cv2.inRange(hsv_roi, np.array(128), np.array(256))
            roi_hist = cv2.calcHist([hsv_roi], [0], mask, [100], [0, 256])
            cv2.normalize(roi_hist, roi_hist, 0, 255, cv2.NORM_MINMAX)
            term_criteria = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 1,
                             1)  # Setup the termination criteria, either 10 iteration or move by atleast 1 pt
            dst = cv2.calcBackProject([opening], [0], roi_hist, [0, 256], 1)
            ret, track_window = cv2.CamShift(dst, track_window, term_criteria)

            # Process POST Tracking
            pts = cv2.boxPoints(ret)
            pts = np.int0(pts)
            img2 = cv2.polylines(frameForView, [pts], True, people.color, 2)
            pos = sum(pts) / len(pts)
            isFound = False
            for dC in detectedContours:
                if dC.x - toleranceRange < pos[0] < dC.x + dC.w + toleranceRange \
                        and dC.y - toleranceRange < pos[1] < dC.y + dC.h + toleranceRange:
                    people.set("x", dC.x)
                    people.set("y", dC.y)
                    people.set("w", dC.w)
                    people.set("h", dC.h)
                    people.set("speed", pos - people.center)
                    people.set("center", pos)
                    people.set("missingCount", 0)
                    detectedContours.remove(dC)
                    isFound = True

                    tR = getExteriorRect(pts)
                    people.set("roi", frame[tR[1]:tR[1] + tR[3], tR[0]:tR[0] + tR[2]])

                    # Process Continuous Tracking
                    prevInStatus = people.isIn
                    currInStatus = checkPosition(boundaryPt1, boundaryPt2, people.center, inCriterion)
                    people.isIn = currInStatus

                    # Check In/Out Status Change
                    if prevInStatus != currInStatus and people.isInChangeFrameCount >= toleranceCountIOStatus:
                        if not allowPassage:
                            passImage = people.roi
                        people.set("isInChangeFrameCount", 0)
                        if currInStatus:
                            peopleIn += 1
                            if not allowPassage:
                                peopleViolationIn += 1
                        else:
                            peopleOut += 1
                            if not allowPassage:
                                peopleViolationOut += 1
                    else:
                        people.set("isInChangeFrameCount", people.isInChangeFrameCount + 1)

            # Process DIS-continuous Tracking
            if not isFound:
                if people.missingCount > toleranceCount:
                    detectedPeople.remove(people)
                else:
                    if checkTouchVSide(people.x + people.speed[0], people.y + people.speed[1], people.w,
                                       people.h, maxWidth, maxHeight, toleranceRange):
                        detectedPeople.remove(people)
                    else:
                        people.set("missingCount", people.missingCount + 1)
                        people.set("x", people.x + people.speed[0])
                        people.set("y", people.y + people.speed[1])
                        people.set("center", people.center + people.speed)

    # Check New People
    for dC in detectedContours:
        if checkTouchVSide(dC.x, dC.y, dC.w, dC.h, maxWidth, maxHeight, toleranceRange):
            startHue += hueIncrementValue
            detectedPeople.append(People(dC.x, dC.y, dC.w, dC.h, frame[dC.y:dC.y + dC.h, dC.x:dC.x + dC.w], startHue))

    # print(str(len(detectedPeople)))
    session.execute("insert into densely.data (timestamp , frame_no , people) values ("+str(int(time.time()))+", "+str(count)+", "+str(len(detectedPeople))+");")
    if(count == frame_no):
        # print('Answer')
        print(str(len(detectedPeople)))
        getAnswer(str(len(detectedPeople)))

    # RE-set
    detectedContours = []
    pFrame = frame
    pNoBg = noBg
    pOpening = opening
    frameCounter += 1


cap.release()
cv2.destroyAllWindows()

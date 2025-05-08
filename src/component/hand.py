import cv2
import mediapipe as mp
import math

class HandDetector:
    def __init__(self, mode=False, max_num_hands=1, min_detection_confidence=0.75, min_tracking_confidence=0.75):
        self.mode = mode
        self.max_num_hands = max_num_hands
        self.min_detection_confidence = min_detection_confidence
        self.min_tracking_confidence = min_tracking_confidence

        self.nmHands = mp.solutions.hands
        self.hands = self.nmHands.Hands(
            static_image_mode=self.mode,
            max_num_hands=self.max_num_hands,
            min_detection_confidence=self.min_detection_confidence,
            min_tracking_confidence=self.min_tracking_confidence
        )
        self.mpDraw = mp.solutions.drawing_utils

    def findHands(self, img, draw=True):
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.result = self.hands.process(imgRGB)
        if self.result.multi_hand_landmarks:
            for handLms in self.result.multi_hand_landmarks:
                if draw:
                    self.mpDraw.draw_landmarks(img, handLms, self.nmHands.HAND_CONNECTIONS)
        return img

    def findPosition(self, img, draw=True):
        lmList = []
        if self.result.multi_hand_landmarks:
            for handLms in self.result.multi_hand_landmarks:
                handLmList = []
                for id, lm in enumerate(handLms.landmark):
                    h, w, c = img.shape
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    handLmList.append([id, cx, cy])
                    if id in [4, 8, 12, 16, 20] and draw:
                        cv2.circle(img, (cx, cy), 10, (255, 0, 0), cv2.FILLED)
                lmList.append(handLmList)
        return lmList
    
    def findDistance(self, p1, p2, img, lmList, draw=True):
        x1, y1 = lmList[p1][1], lmList[p1][2]
        x2, y2 = lmList[p2][1], lmList[p2][2]
        length = math.hypot(x2 - x1, y2 - y1)
        if draw:
            cv2.line(img, (x1, y1), (x2, y2), (255, 0, 255), 3)
            cv2.circle(img, (x1, y1), 10, (0, 255, 0), cv2.FILLED)
            cv2.circle(img, (x2, y2), 10, (0, 255, 0), cv2.FILLED)
        return length, img
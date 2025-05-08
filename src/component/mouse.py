import cv2
import pyautogui
from time import time
from component.hand import HandDetector

class VirtualMouse:
    def __init__(self, detector):
        self.detector = detector
        self.screen_width, self.screen_height = pyautogui.size()
        self.prev_x, self.prev_y = 0, 0
        self.pTime = 0

    def process(self, img, lmList):
        cTime = time()
        fps = 1 / (cTime - self.pTime) if self.pTime != 0 else 0
        self.pTime = cTime

        if lmList and len(lmList[0]) > 8:
            x, y = lmList[0][8][1], lmList[0][8][2]  # Index finger tip
            if self.prev_x != 0 and self.prev_y != 0:
                dx = x - self.prev_x
                dy = y - self.prev_y
                # dx = -dx  # Invert x-direction
                screen_x = int(self.screen_width * (dx / img.shape[1]))
                screen_y = int(self.screen_height * (dy / img.shape[0]))
                pyautogui.moveRel(screen_x, screen_y)
            self.prev_x, self.prev_y = x, y

        cv2.putText(img, f"FPS: {int(fps)}", (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 255), 2)
        return img
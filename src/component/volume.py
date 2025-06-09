import cv2
import numpy as np
from component.hand import HandDetector
import subprocess

COLOR_DEFAULT = (50, 150, 200)      # Xanh dương nhạt (mặc định)
COLOR_HIGHLIGHTED = (100, 200, 255) # Xanh dương sáng (khi trỏ vào)
COLOR_SELECTED = (0, 180, 150)      # Xanh ngọc (khi chọn)
COLOR_TEXT = (255, 255, 255)        # Trắng (màu chữ)

class VirtualVolume:
    def __init__(self, detector, pos=[640, 360], size=[300, 50]):
        self.detector = detector
        self.pos = pos
        self.size = size
        self.volume = 50  # Giá trị âm lượng ban đầu

    def set_volume(self, volume):
        subprocess.run(["amixer", "-q", "set", "Master", f"{int(volume)}%"])

    def process(self, img, lmList):
        if lmList and len(lmList[0]) > 8:
            index_tip = lmList[0][8][1:3]
            thumb_tip = lmList[0][4][1:3]
            distance, img = self.detector.findDistance(8, 4, img, lmList[0])

            # Ánh xạ khoảng cách
            max_distance = 200
            self.volume = np.interp(distance, [20, max_distance], [0, 100])
            self.volume = max(0, min(100, self.volume))

            # Điều chỉnh âm lượng
            self.set_volume(self.volume)

        return img

    def draw(self, img):
        imgNew = np.zeros_like(img, np.uint8)
        x, y = self.pos[0] - self.size[0] // 2, self.pos[1] - self.size[1] // 2
        w, h = self.size

        cv2.rectangle(imgNew, (x, y), (x + w, y + h), COLOR_DEFAULT, cv2.FILLED)
        fill_width = int(w * (self.volume / 100))
        cv2.rectangle(imgNew, (x, y), (x + fill_width, y + h), COLOR_SELECTED, cv2.FILLED)
        cv2.putText(imgNew, f"Volume: {int(self.volume)}%", (x + 10, y + h - 10), 
                    cv2.FONT_HERSHEY_PLAIN, 1.5, COLOR_TEXT, 2)

        out = img.copy()
        alpha = 0.5
        mask = imgNew.astype(bool)
        out[mask] = cv2.addWeighted(img, alpha, imgNew, 1 - alpha, 0)[mask]
        return out
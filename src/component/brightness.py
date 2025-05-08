import cv2
import numpy as np
from component.hand import HandDetector
import platform
import screen_brightness_control as sbc
import subprocess

# Quy định màu lạnh
COLOR_DEFAULT = (50, 150, 200)
COLOR_HIGHLIGHTED = (100, 200, 255)
COLOR_SELECTED = (0, 180, 150)
COLOR_TEXT = (255, 255, 255)

class VirtualBrightness:
    def __init__(self, detector, pos=[640, 360], size=[300, 50]):
        self.detector = detector
        self.pos = pos
        self.size = size
        self.brightness = 50  # Giá trị ban đầu
        self.system = platform.system()

        # Tự động tìm tên màn hình trên Linux
        if self.system == "Linux":
            try:
                output = subprocess.check_output(["xrandr", "--current"]).decode("utf-8")
                for line in output.splitlines():
                    if " connected" in line and "*" in line:
                        self.display_name = line.split()[0]
                        print(f"Detected display: {self.display_name}")
                        break
                else:
                    self.display_name = "eDP-1"  # Giá trị mặc định nếu không tìm thấy
                    print("Không tìm thấy màn hình hoạt động, dùng mặc định: eDP-1")
            except Exception as e:
                self.display_name = "eDP-1"
                print(f"Lỗi khi tìm màn hình: {e}")
        else:
            self.display_name = None  # Không cần trên Windows/macOS

    def set_brightness(self, brightness):
        try:
            sbc.set_brightness(int(brightness))
            print(f"Set brightness to {int(brightness)}% using screen-brightness-control")
        except Exception as e:
            print(f"screen-brightness-control failed: {e}")
            if self.system == "Linux" and self.display_name:
                brightness_value = brightness / 100
                subprocess.run(["xrandr", "--output", self.display_name, "--brightness", str(brightness_value)])
                print(f"Set brightness to {brightness_value} using xrandr on {self.display_name}")

    def process(self, img, lmList):
        if lmList and len(lmList[0]) > 8:
            index_tip = lmList[0][8][1:3]
            thumb_tip = lmList[0][4][1:3]
            distance, img = self.detector.findDistance(8, 4, img, lmList[0])

            # Ánh xạ khoảng cách
            max_distance = 200
            self.brightness = np.interp(distance, [20, max_distance], [0, 100])
            self.brightness = max(0, min(100, self.brightness))

            # Điều chỉnh độ sáng
            self.set_brightness(self.brightness)

        return img

    def draw(self, img):
        imgNew = np.zeros_like(img, np.uint8)
        x, y = self.pos[0] - self.size[0] // 2, self.pos[1] - self.size[1] // 2
        w, h = self.size

        cv2.rectangle(imgNew, (x, y), (x + w, y + h), COLOR_DEFAULT, cv2.FILLED)
        fill_width = int(w * (self.brightness / 100))
        cv2.rectangle(imgNew, (x, y), (x + fill_width, y + h), COLOR_SELECTED, cv2.FILLED)
        cv2.putText(imgNew, f"Brightness: {int(self.brightness)}%", (x + 10, y + h - 10), 
                    cv2.FONT_HERSHEY_PLAIN, 1.5, COLOR_TEXT, 2)

        out = img.copy()
        alpha = 0.5
        mask = imgNew.astype(bool)
        out[mask] = cv2.addWeighted(img, alpha, imgNew, 1 - alpha, 0)[mask]
        return out
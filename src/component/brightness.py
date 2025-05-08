import cv2
import numpy as np
from component.hand import HandDetector
import subprocess

# Quy định màu sắc
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
        self.last_brightness = None  # Lưu giá trị độ sáng trước đó
        self.display_name = self._get_display_name()

    def _get_display_name(self):
        """Tìm tên màn hình hoạt động bằng xrandr."""
        try:
            output = subprocess.check_output(["xrandr", "--current"]).decode("utf-8")
            for line in output.splitlines():
                if " connected" in line and "*" in line:
                    display_name = line.split()[0]
                    print(f"Đã tìm thấy màn hình: {display_name}")
                    return display_name
            print("Không tìm thấy màn hình hoạt động, dùng mặc định: eDP-1")
            return "eDP-1"  # Màn hình mặc định trên laptop
        except Exception as e:
            print(f"Lỗi khi tìm màn hình: {e}")
            return "eDP-1"

    def set_brightness(self, brightness):
        """Điều chỉnh độ sáng màn hình bằng xrandr."""
        brightness = max(0, min(100, int(brightness)))  # Giới hạn 0-100%
        if self.last_brightness == brightness:
            return  # Không làm gì nếu độ sáng không thay đổi
        try:
            brightness_value = brightness / 100  # xrandr dùng giá trị từ 0.0 đến 1.0
            subprocess.run(
                ["xrandr", "--output", self.display_name, "--brightness", str(brightness_value)],
                check=True
            )
            print(f"Đã đặt độ sáng {brightness}% bằng xrandr trên {self.display_name}")
            self.last_brightness = brightness
        except subprocess.CalledProcessError as e:
            print(f"xrandr thất bại: {e}")

    def process(self, img, lmList):
        """Xử lý cử chỉ tay để điều chỉnh độ sáng."""
        if lmList and len(lmList[0]) > 8:
            index_tip = lmList[0][8][1:3]
            thumb_tip = lmList[0][4][1:3]
            distance, img = self.detector.findDistance(8, 4, img, lmList[0])

            # Ánh xạ khoảng cách thành độ sáng
            max_distance = 200
            self.brightness = np.interp(distance, [20, max_distance], [0, 100])
            self.brightness = max(0, min(100, self.brightness))

            # Cập nhật độ sáng
            self.set_brightness(self.brightness)

        return img

    def draw(self, img):
        """Vẽ thanh điều chỉnh độ sáng."""
        imgNew = np.zeros_like(img, np.uint8)
        x, y = self.pos[0] - self.size[0] // 2, self.pos[1] - self.size[1] // 2
        w, h = self.size

        # Vẽ thanh nền
        cv2.rectangle(imgNew, (x, y), (x + w, y + h), COLOR_DEFAULT, cv2.FILLED)
        # Vẽ phần độ sáng hiện tại
        fill_width = int(w * (self.brightness / 100))
        cv2.rectangle(imgNew, (x, y), (x + fill_width, y + h), COLOR_SELECTED, cv2.FILLED)
        # Hiển thị giá trị độ sáng
        cv2.putText(imgNew, f"Do sang: {int(self.brightness)}%", (x + 10, y + h - 10), 
                    cv2.FONT_HERSHEY_PLAIN, 1.5, COLOR_TEXT, 2)

        # Kết hợp với ảnh gốc
        out = img.copy()
        alpha = 0.5
        mask = imgNew.astype(bool)
        out[mask] = cv2.addWeighted(img, alpha, imgNew, 1 - alpha, 0)[mask]
        return out
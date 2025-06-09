import cv2
import numpy as np
from component.hand import HandDetector
from component.keyboard import Button

# Quy định màu lạnh mới cho các nút
COLOR_DEFAULT = (50, 150, 200)      # Xanh dương nhạt (mặc định)
COLOR_HIGHLIGHTED = (100, 200, 255) # Xanh dương sáng (khi trỏ vào)
COLOR_SELECTED = (0, 180, 150)      # Xanh ngọc (khi chọn)
COLOR_TEXT = (255, 255, 255)        # Trắng (màu chữ)
COLOR_TEXTBOX = (80, 120, 160)      # Xanh xám nhạt (hộp văn bản)

class mulDevice:
    def __init__(self, detector, frame_width, frame_height, button_size=[100, 25]):
        self.detector = detector
        self.frame_width = frame_width
        self.frame_height = frame_height
        self.button_size = button_size
        self.options = ["Mouse", "Keyboard", "Volume", "Brightness", "Pr_Number"]
        self.selected_option = None
        self.buttonList = self._create_buttons()
        self.isDragging = False

    def _create_buttons(self):
        buttonList = []
        center_y = self.frame_height // 2  
        gap = 20  
        start_x = 0  

        total_height = 4 * self.button_size[1] + 3 * gap
        start_y = center_y - total_height // 2 

        # Nút Mouse
        buttonList.append(Button([start_x, start_y], "Mouse", self.button_size))

        # Nút Keyboard
        keyboard_y = start_y + self.button_size[1] + gap
        buttonList.append(Button([start_x, keyboard_y], "Keyboard", self.button_size))

        # Nút Volume
        volume_y = keyboard_y + self.button_size[1] + gap
        buttonList.append(Button([start_x, volume_y], "Volume", self.button_size))

        # Nút Brightness
        brightness_y = volume_y + self.button_size[1] + gap
        buttonList.append(Button([start_x, brightness_y], "Brightness", self.button_size))

        # Nút Predict Number
        predict_y = brightness_y + self.button_size[1] + gap
        buttonList.append(Button([start_x, predict_y], "Pr_Number", self.button_size))

        return buttonList

    def reset(self):
        self.buttonList = self._create_buttons()
        self.isDragging = False
        self.selected_option = None

    def update(self, cursor, is_pinching):
        for button in self.buttonList:
            x, y = button.pos
            w, h = button.size
            if x < cursor[0] < x + w and y < cursor[1] < y + h and is_pinching:
                self.isDragging = True
                self.selected_option = button.text
        if not is_pinching:
            self.isDragging = False

    def process(self, img, lmList):
        highlighted_button = None
        selected_button = None

        if lmList and len(lmList[0]) > 8:
            index_tip = lmList[0][8][1:3]
            thumb_tip = lmList[0][4][1:3]
            distance, img = self.detector.findDistance(8, 4, img, lmList[0])
            is_pinching = distance < 30
            cursor = [(index_tip[0] + thumb_tip[0]) // 2, (index_tip[1] + thumb_tip[1]) // 2]
            self.update(cursor, is_pinching)

            for button in self.buttonList:
                x, y = button.pos
                w, h = button.size
                if x < index_tip[0] < x + w and y < index_tip[1] < y + h:
                    highlighted_button = button
                    if is_pinching:
                        selected_button = button
                        self.selected_option = button.text

        return img, highlighted_button, selected_button

    def draw(self, img, highlighted_button=None, selected_button=None):
        imgNew = np.zeros_like(img, np.uint8)
        for button in self.buttonList:
            x, y = button.pos
            color = COLOR_DEFAULT
            if button == selected_button:
                color = COLOR_SELECTED
                cv2.rectangle(imgNew, (x-5, y-5), (x + button.size[0] + 5, y + button.size[1] + 5), color, cv2.FILLED)
            elif button == highlighted_button:
                color = COLOR_HIGHLIGHTED
                cv2.rectangle(imgNew, (x-5, y-5), (x + button.size[0] + 5, y + button.size[1] + 5), color, cv2.FILLED)
            cv2.rectangle(imgNew, (x, y), (x + button.size[0], y + button.size[1]), color, cv2.FILLED)
            cv2.putText(imgNew, button.text, (x + 10, y + button.size[1] - 10), cv2.FONT_HERSHEY_PLAIN, 1, COLOR_TEXT, 2)

        out = img.copy()
        alpha = 0.5
        mask = imgNew.astype(bool)
        out[mask] = cv2.addWeighted(img, alpha, imgNew, 1 - alpha, 0)[mask]
        return out
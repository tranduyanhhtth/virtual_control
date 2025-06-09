import cv2
import numpy as np
from time import time
from pynput.keyboard import Controller
from component.hand import HandDetector
import math

COLOR_DEFAULT = (50, 150, 200)      # Xanh dương nhạt (mặc định)
COLOR_HIGHLIGHTED = (100, 200, 255) # Xanh dương sáng (khi trỏ vào)
COLOR_SELECTED = (0, 180, 150)      # Xanh ngọc (khi chọn)
COLOR_TEXT = (255, 255, 255)        # Trắng (màu chữ)
COLOR_TEXTBOX = (80, 120, 160)      # Xanh xám nhạt (hộp văn bản)
    
class Button:
    def __init__(self, pos, text, size):
        self.pos = pos
        self.text = text
        self.size = size

class VirtualKeyboard:
    def __init__(self, detector, pos=[320, 240], size=[400, 150]):
        self.detector = detector
        self.pos = pos
        self.size = size
        self.isDragging = False
        self.keyboard = Controller()
        self.keys = [
            ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"],
            ["Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P"],
            ["A", "S", "D", "F", "G", "H", "J", "K", "L", ";"],
            ["Z", "X", "C", "V", "B", "N", "M", ",", ".", "/"],
            ["Backspace", " ", "Enter"]
        ]
        self.finalText = ""
        self.buttonList = self._create_buttons()
        self.last_press_time = 0
        self.debounce_delay = 0.3

    def _create_buttons(self):
        buttonList = []
        num_rows = len(self.keys)
        key_height = self.size[1] // num_rows  # Chiều cao cố định cho mỗi hàng
        num_cols = 10  # Số cột tối đa dựa trên hàng dài nhất
        key_width = self.size[0] // num_cols  # Chiều rộng cố định cho mỗi phím

        for i, row in enumerate(self.keys):
            row_length = len(row)
            if i < num_rows - 1:  # For regular rows (not the last row)
                start_x = self.pos[0] - self.size[0] // 2 + (num_cols - row_length) * key_width // 2  # Căn giữa hàng
                for j, key in enumerate(row):
                    x = start_x + j * key_width
                    y = self.pos[1] - self.size[1] // 2 + i * key_height
                    button_width = key_width
                    buttonList.append(Button([x, y], key, [button_width - 5, key_height - 5]))
            else:
                total_special_width = (2 * key_width) + (4 * key_width) + (2 * key_width)  # Backspace (2x), Space (4x), Enter (2x)
                start_x = self.pos[0] - self.size[0] // 2 + (self.size[0] - total_special_width) // 2  # Center the special keys

                current_x = start_x - key_width  
                for j, key in enumerate(row):
                    y = self.pos[1] - self.size[1] // 2 + i * key_height
                    if key == " ":
                        button_width = key_width * 4  # Space key is 4x wider
                    elif key in ["Backspace", "Enter"]:
                        button_width = key_width * 3  # Backspace and Enter are 2x wider
                    else:
                        button_width = key_width
                    buttonList.append(Button([current_x, y], key, [button_width - 5, key_height - 5]))
                    current_x += button_width  # Update the x position for the next key

        return buttonList
    
    def _is_open_hand(self, lmList):
        if len(lmList) < 21:
            return False
        wrist = lmList[0][1:3]
        finger_tips = [lmList[i][1:3] for i in [4, 8, 12, 16, 20]]
        open_threshold = 150
        distances = [math.hypot(tip[0] - wrist[0], tip[1] - wrist[1]) for tip in finger_tips]
        return all(dist > open_threshold for dist in distances)

    def update_position(self, cursor, is_open_hand):
        cx, cy = self.pos
        w, h = self.size
        if cx - w // 2 < cursor[0] < cx + w // 2 and cy - h // 2 < cursor[1] < cy + h // 2:
            if is_open_hand:
                self.isDragging = True
        else:
            if not is_open_hand:
                self.isDragging = False
        if self.isDragging and is_open_hand:
            self.pos = cursor
            self.buttonList = self._create_buttons()

    def process(self, img, lmList):
        highlighted_button = None
        selected_button = None
        current_time = time()

        if lmList and len(lmList[0]) > 20:
            index_tip = lmList[0][8][1:3]
            thumb_tip = lmList[0][4][1:3]
            distance, img = self.detector.findDistance(8, 4, img, lmList[0])
            is_pinching = distance < 20
            is_open_hand = self._is_open_hand(lmList[0])
            cursor = [(index_tip[0] + thumb_tip[0]) // 2, (index_tip[1] + thumb_tip[1]) // 2]

            if is_open_hand:
                self.update_position(cursor, is_open_hand)
            elif not is_open_hand:
                for button in self.buttonList:
                    x, y = button.pos
                    w, h = button.size
                    if x < index_tip[0] < x + w and y < index_tip[1] < y + h:
                        highlighted_button = button
                        if is_pinching and (current_time - self.last_press_time) > self.debounce_delay:
                            selected_button = button
                            if button.text == "Backspace":
                                self.finalText = self.finalText[:-1]
                                self.keyboard.press('\b')
                            elif button.text == "Enter":
                                self.finalText += "\n"
                                self.keyboard.press('\n')
                            elif button.text == " ":
                                self.finalText += " "
                                self.keyboard.press(' ')
                            else:
                                self.keyboard.press(button.text)
                                self.finalText += button.text
                            self.last_press_time = current_time

        return img, highlighted_button, selected_button

    def draw_keyboard(self, img, buttonList, highlighted_button=None, selected_button=None, pos=[320, 240], size=[400, 150], finalText=""):
        imgNew = np.zeros_like(img, np.uint8)
        for button in buttonList:
            x, y = button.pos
            color = COLOR_DEFAULT
            if button == selected_button:
                color = COLOR_SELECTED
                cv2.rectangle(imgNew, (x-5, y-5), (x + button.size[0] + 5, y + button.size[1] + 5), color, cv2.FILLED)
            elif button == highlighted_button:
                color = COLOR_HIGHLIGHTED
                cv2.rectangle(imgNew, (x-5, y-5), (x + button.size[0] + 5, y + button.size[1] + 5), color, cv2.FILLED)
            cv2.rectangle(imgNew, (x, y), (x + button.size[0], y + button.size[1]), color, cv2.FILLED)
            cv2.putText(imgNew, button.text, (x + 5, y + button.size[1] - 5), cv2.FONT_HERSHEY_PLAIN, 1.2, COLOR_TEXT, 2)
        
        text_x = pos[0] - size[0] // 2
        text_y = pos[1] - size[1] // 2 - 40
        cv2.rectangle(imgNew, (text_x, text_y), (text_x + size[0], text_y + 30), COLOR_TEXTBOX, cv2.FILLED)
        cv2.putText(imgNew, finalText, (text_x + 5, text_y + 20), cv2.FONT_HERSHEY_PLAIN, 1.5, COLOR_TEXT, 2)

        out = img.copy()
        alpha = 0.5
        mask = imgNew.astype(bool)
        out[mask] = cv2.addWeighted(img, alpha, imgNew, 1 - alpha, 0)[mask]
        return out



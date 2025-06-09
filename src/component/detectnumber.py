import mediapipe as mp
from mediapipe import solutions as mp_solutions
import cv2

class DetectNumber:
    def __init__(self):
        self.mp_hands = mp_solutions.hands
        self.hands = self.mp_hands.Hands(static_image_mode=False, max_num_hands=1, min_detection_confidence=0.5)
        self.mp_draw = mp_solutions.drawing_utils
    
    def release(self):
        self.hands.close()
        cv2.destroyAllWindows()

    def get_hand_landmarks(self, img):
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = self.hands.process(img_rgb)

        if results.multi_hand_landmarks:
            hand_landmarks = results.multi_hand_landmarks[0]
            landmarks = [(landmark.x, landmark.y) for landmark in hand_landmarks.landmark]
            return landmarks
        else:
            return None
        
    def get_hand_number(self, img):
        landmarks = self.get_hand_landmarks(img)
        if landmarks is None:
            return None

        # Kiểm tra vị trí ngón cái (duỗi thẳng hay gập lại); (đầu ngón thấp hơn khớp PIP)
        thumb_extended = landmarks[4][0] < landmarks[3][0]  # Đầu ngón cái (4) ở bên trái của khớp ngón cái (3)
        index_extended = landmarks[8][1] < landmarks[6][1]   # Ngón trỏ
        middle_extended = landmarks[12][1] < landmarks[10][1]  # Ngón giữa
        ring_extended = landmarks[16][1] < landmarks[14][1]   # Ngón đeo nhẫn
        pinky_extended = landmarks[20][1] < landmarks[18][1]  # Ngón út

        # Số 0: Nắm tay chặt, tất cả các ngón tay gập lại
        if not thumb_extended and not index_extended and not middle_extended and not ring_extended and not pinky_extended:
            return 0

        # Số 1: Chỉ ngón trỏ giơ lên
        if index_extended and not middle_extended and not ring_extended and not pinky_extended and not thumb_extended:
            return 1

        # Số 2: Giơ ngón trỏ và ngón giữa (dấu hiệu chữ V)
        if index_extended and middle_extended and not ring_extended and not pinky_extended and not thumb_extended:
            return 2

        # Số 3: Giơ ngón trỏ, ngón giữa và ngón cái
        if index_extended and middle_extended and thumb_extended and not ring_extended and not pinky_extended:
            return 3

        # Số 4: Giơ ngón trỏ, ngón giữa, ngón đeo nhẫn và ngón út
        if index_extended and middle_extended and ring_extended and pinky_extended and not thumb_extended:
            return 4

        # Số 5: Xòe cả bàn tay, tất cả ngón tay giơ lên
        if index_extended and middle_extended and ring_extended and pinky_extended and thumb_extended:
            return 5

        # Số 6: Giơ ngón trỏ, ngón giữa và ngón đeo nhẫn
        if index_extended and middle_extended and ring_extended and not pinky_extended and not thumb_extended:
            return 6

        # Số 7: Giơ ngón trỏ, ngón giữa và ngón út
        if index_extended and middle_extended and pinky_extended and not ring_extended and not thumb_extended:
            return 7

        # Số 8: Giơ ngón trỏ, ngón đeo nhẫn và ngón út
        if index_extended and ring_extended and pinky_extended and not middle_extended and not thumb_extended:
            return 8

        # Số 9: Giơ ngón giữa, ngón đeo nhẫn và ngón út
        if middle_extended and ring_extended and pinky_extended and not index_extended and not thumb_extended:
            return 9
        return None
    
    # def get_hand_number_from_camera(self):
    #     cap = cv2.VideoCapture(0)
    #     if not cap.isOpened():
    #         print("Error: Could not open camera.")
    #         return None

    #     while True:
    #         ret, frame = cap.read()
    #         if not ret:
    #             break

    #         frame = cv2.flip(frame,1)
    #         number = self.get_hand_number(frame)
    #         if number is not None and 0 <= number <= 9:
    #             text = f"Predict number: {number}"
    #         else:
    #             text = ""

    #         cv2.putText(frame, text, (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 4)

    #         cv2.imshow('Camera', frame)
    #         if cv2.waitKey(1) & 0xFF == ord('q'):
    #             break

    #     cap.release()
    #     cv2.destroyAllWindows()
    #     return number

    def process(self, img):
        number = self.get_hand_number(img)
        if number is not None and 0 <= number <= 9:
            text = f"Predict number: {number}"
        else:
            text = ""
        cv2.putText(img, text, (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 4)
        return img
    
# if __name__ == "__main__":
#     detector = DetectNumber()
#     detector.get_hand_number_from_camera()
#     detector.release()
import cv2
from component.hand import HandDetector
from component.keyboard import VirtualKeyboard
from component.mouse import VirtualMouse
from component.volume import VirtualVolume
from component.brightness import VirtualBrightness
from component.multhread import mulDevice
from component.detectnumber import DetectNumber

def main():
    cv2.setUseOptimized(True)
    cap = cv2.VideoCapture(0)
    frame_width = 1280
    frame_height = 720
    cap.set(3, frame_width)
    cap.set(4, frame_height)
    cap.set(cv2.CAP_PROP_FPS, 60)

    # Lấy kích thước thực tế từ camera
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    detector = HandDetector()
    menu = mulDevice(detector, frame_width, frame_height)
    keyboard = VirtualKeyboard(detector)
    mouse = VirtualMouse(detector)
    volume = VirtualVolume(detector)
    brightness = VirtualBrightness(detector)
    detect_number = DetectNumber()

    show_menu = True

    while True:
        success, img = cap.read()
        if not success:
            continue

        img = cv2.flip(img, 1)
        img = detector.findHands(img)
        lmList = detector.findPosition(img)

        # Kiểm tra tay trong khung hình
        if not lmList or len(lmList) == 0:
            show_menu = True
            menu.reset()

        # Nếu menu đang hiển thị
        if show_menu:
            img, highlighted_button, selected_button = menu.process(img, lmList)
            img = menu.draw(img, highlighted_button, selected_button)
            if menu.selected_option:
                show_menu = False
        # Nếu menu không hiển thị, xử lý tùy chọn đã chọn
        else:
            if menu.selected_option == "Keyboard":
                img, highlighted_button, selected_button = keyboard.process(img, lmList)
                img = keyboard.draw_keyboard(img, keyboard.buttonList, highlighted_button, selected_button, keyboard.pos, keyboard.size, keyboard.finalText)
            elif menu.selected_option == "Mouse":
                img = mouse.process(img, lmList)
            elif menu.selected_option == "Volume":
                img = volume.process(img, lmList)
                img = volume.draw(img)
            elif menu.selected_option == "Brightness":
                img = brightness.process(img, lmList)
                img = brightness.draw(img)
            elif menu.selected_option == "Pr_Number":
                img = detect_number.process(img)

        cv2.imshow("Image", img)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
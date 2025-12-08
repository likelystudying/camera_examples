from picamera2 import Picamera2
import cv2
import sys
import select

class CameraLib:
    def __init__(self, width=640, height=480, rotate_180=True):
        self.rotate_180 = rotate_180
        self.picam2 = Picamera2()
        config = self.picam2.create_preview_configuration(
            main={"format": "RGB888", "size": (width, height)}
            )
        self.picam2.configure(config)
        self.picam2.start()
        return
    
    def get_frame(self):
        frame = self.picam2.capture_array()
        if self.rotate_180:
            frame = cv2.rotate(frame, cv2.ROTATE_180)
        return frame

    def preview(self, window_name = "Camera"):
        frame = self.get_frame()
        cv2.imshow(window_name, frame)
        cv2.waitKey(1)
        return frame
    
    def capture(self, filename="image.jpg"):
        frame = self.get_frame()
        cv2.imwrite(filename, frame)
        return filename

    def close(self):
        try:
            self.picam2.stop()
            cv2.destroyAllWindows()
        except Exception:
            pass

    def __del__(self):
        try:
            self.picam2.stop()
            cv2.destroyAllWindows()
        except Exception:
            pass

def test():
    import sys
    import select
    def kbhit():
        return select.select([sys.stdin], [], [], 0)[0]
    
    cam = CameraLib(width=640, height=480, rotate_180=True)

    print("Press 'c' to capture, 'q' to quit.")
    while True:
        frame = cam.preview()
        if kbhit():
            cmd = sys.stdin.readline().strip()
            if cmd == "q":
                break
            elif cmd == "c":
                cam.capture("image.jpg")
                print("Saved image.jpg")
            else:
                print("Not supported:", cmd)

    cam.close()


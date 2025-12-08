import cv2
from CameraLib import CameraLib
from ServoLib import ServoLib



class Facetrack:
    def __init__(self):
        print("Initializing facetracker...")

        # Camera. 180==true because Pi Camera is mounted upside down...
        self.cam = CameraLib(width=640, height=480, rotate_180=True)

        # Servo
        self.servo = ServoLib("face-servo", 18)

        # Correct Haar path for Raspberry Pi OS packages
        haar_path = "/usr/share/opencv4/haarcascades/haarcascade_frontalface_default.xml"

        self.detector = cv2.CascadeClassifier(haar_path)

        if self.detector.empty():
            raise RuntimeError("Failed to load Haar cascade: " + haar_path)

    def process_frame(self, window_name="Facetrack"):
        frame = self.cam.get_frame()

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.detector.detectMultiScale(gray, 1.3, 5)

        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

        # Show frame
        cv2.imshow(window_name, frame)
        cv2.waitKey(1)

        return frame, faces

    def track(self):
        print("Tracking started. Press CTRL+C to stop.")

        while True:
            frame, faces = self.process_frame()

            if len(faces) > 0:
                (x, y, w, h) = faces[0]

                face_center = x + w/2
                frame_center = frame.shape[1] / 2

                error = (face_center - frame_center) / frame_center
                target_angle = 90 + error * 40

                self.servo.set_angle(target_angle, steps=3)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        self.cleanup()

    def cleanup(self):
        print("Cleaning up...")
        self.cam.close()
        self.servo.stop_servo()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    ft = Facetrack()
    ft.track()

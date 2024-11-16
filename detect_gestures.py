""" Code built on the response at https://stackoverflow.com/questions/76320300/nameerror-name-mp-image-is-not-defined-with-mediapipe-gesture-recognition """

# Standard library imports
import random
import threading

# External imports
import cv2
import mediapipe as mp
from mediapipe.tasks import python

gestures = ["Pointing_Up", "Closed_Fist", "Open_Palm", "ILoveYou", "Victory"]
model_path = "gesture_recognizer.task"

class GestureRecognizer:
    def main(self):
        
        GestureRecognizer = mp.tasks.vision.GestureRecognizer
        GestureRecognizerOptions = mp.tasks.vision.GestureRecognizerOptions
        VisionRunningMode = mp.tasks.vision.RunningMode
        
        
        self.gesture_to_do = random.choice(gestures)
        self.points = 0

        self.lock = threading.Lock()
        self.current_gestures = []
        
        options = GestureRecognizerOptions(
            base_options=python.BaseOptions(model_asset_path=model_path),
            running_mode=VisionRunningMode.LIVE_STREAM,
            num_hands = 1,
            result_callback=self.__result_callback)
        recognizer = GestureRecognizer.create_from_options(options)

        timestamp = 0 
        mp_drawing = mp.solutions.drawing_utils
        mp_hands = mp.solutions.hands
        hands = mp_hands.Hands(
                static_image_mode=False,
                max_num_hands=1,
                min_detection_confidence=0.65,
                min_tracking_confidence=0.65)

        cap = cv2.VideoCapture(0)

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = hands.process(frame)
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            np_array = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=np_array)
                    recognizer.recognize_async(mp_image, timestamp)
                    timestamp = timestamp + 1 # should be monotonically increasing, because in LIVE_STREAM mode
 
                self.add_gesture_label_to_video(frame)

            cv2.imshow('MediaPipe Hands', frame)
            if cv2.waitKey(1) & 0xFF == 27:
                break

        cap.release()

    def add_gesture_label_to_video(self, frame):
        """ Displays the most recently recognised hand gesture in the top left corner of the stream. """
        self.lock.acquire()
        gestures = self.current_gestures
        self.lock.release()
        y_pos = 50
        for hand_gesture_name in gestures:
            # show the prediction on the frame
            cv2.putText(frame, hand_gesture_name, (10, y_pos), cv2.FONT_HERSHEY_SIMPLEX,
                                1, (0,0,255), 2, cv2.LINE_AA)
            y_pos += 50

    def __result_callback(self, result, output_image, timestamp_ms):

        self.lock.acquire() # solves potential concurrency issues
        self.current_gestures = []
        if result is not None and any(result.gestures):
            print("Recognized gestures:")
            for single_hand_gesture_data in result.gestures:
                gesture_name = single_hand_gesture_data[0].category_name
                print(gesture_name)
                self.current_gestures.append(gesture_name)
                
                if gesture_name == self.gesture_to_do:
                    self.points += 1
                    self.gesture_to_do = random.choice(gestures)
            
            print("points", self.points)
            print("to do", self.gesture_to_do)
        self.lock.release()

rec = GestureRecognizer()
rec.main()

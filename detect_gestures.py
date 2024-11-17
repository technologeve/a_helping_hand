""" Game designed to encourage rehabilitation after hand and wrist injuries.

    Code built on the response at 
    https://stackoverflow.com/questions/76320300/nameerror-name-mp-image-is-not-defined-with-mediapipe-gesture-recognition """

# Standard library imports
import os
import argparse
import random
import threading

# External imports
import cv2
import mediapipe as mp
from playsound import playsound
from mediapipe.tasks import python

gestures = ["Pointing_Up", "Closed_Fist", "Open_Palm", 
            "ILoveYou", "Victory", "Thumb_Up", "Thumb_Down"]
model_path = "gesture_recognizer.task"
gesture_readable = {"Pointing_Up": "Point finger", "Closed_Fist": "closed fist",
                    "Open_Palm": "Open hand", "ILoveYou": "I love you",
                    "Victory": "Peace sign", "Thumb_Up": "Thumbs up", 
                    "Thumb_Down": "Thumbs down"}

def preload_images():
    """ Load gesture images and masks in advance. """
    
    images = {}
    masks = {}

    for gesture in gestures:
        # Load image
        current_image = cv2.imread(os.path.join("images", gesture + ".png"))

        # Resize to 300x300
        current_image = cv2.resize(current_image, (300, 300))
        images[gesture] = current_image

        # Create a mask
        _, ret = cv2.threshold(current_image, 1, 255, cv2.THRESH_BINARY)
        masks[gesture] = ret

    return images, masks


def load_astronaut():
    """ Load astronaut image. """

    astro_image = cv2.imread(os.path.join("images",  "astronaut.png"))

    astro = cv2.resize(astro_image, (300, 400))

    # Create a mask
    _, astro_mask = cv2.threshold(astro, 1, 255, cv2.THRESH_BINARY)

    return astro, astro_mask


class HelpingHandGame():
    """ Game, recognising hand gestures. """

    def main(self):
        """ Main game function. """

        GestureRecognizer = mp.tasks.vision.GestureRecognizer
        GestureRecognizerOptions = mp.tasks.vision.GestureRecognizerOptions
        VisionRunningMode = mp.tasks.vision.RunningMode


        self.gesture_to_do = random.choice(gestures)
        self.points = 0

        self.lock = threading.Lock()
        self.current_gestures = []

        self.images, self.masks = preload_images()
        self.astro, self.astro_mask = load_astronaut()

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
                    timestamp += 1

                self.display_goal_gesture(frame)

            cv2.imshow('MediaPipe Hands', frame)
            if cv2.waitKey(1) & 0xFF == 27:
                break

        cap.release()

    def display_goal_gesture(self, frame):
        """ Displays the most recently recognised hand gesture in the top left corner of the stream. """

        self.lock.acquire()
        goal_gesture = self.gesture_to_do
        user_score = self.points
        self.lock.release()

        # Use text to say goal gesture
        cv2.rectangle(frame, (5, 10), (450, 80), (102,47,32), -1)
        cv2.putText(frame, "Goal gesture: " + gesture_readable[goal_gesture], (10, 50), cv2.FONT_HERSHEY_SIMPLEX,
                                1, (255,255,255), 2, cv2.LINE_AA)

        # Display the goal gesture as an image
        curr_fr = cv2.bitwise_and(frame[100:400, 50:350], cv2.bitwise_not(self.masks[goal_gesture]))
        logo = cv2.bitwise_and(self.images[goal_gesture], self.masks[goal_gesture])
        roi = cv2.bitwise_or(curr_fr, logo)

        frame[100:400, 50:350] = roi

        # Display the astronaut
        curr_fr = cv2.bitwise_and(frame[600:1000, 1450:1750], cv2.bitwise_not(self.astro_mask))
        logo = cv2.bitwise_and(self.astro, self.astro_mask)
        roi = cv2.bitwise_or(curr_fr, logo)

        frame[600:1000, 1450:1750] = roi

        # Display the user's score
        cv2.rectangle(frame, (5, 410), (200, 475), (102,47,32), -1)
        cv2.putText(frame, "Score: " + str(user_score), (13, 450), cv2.FONT_HERSHEY_SIMPLEX,
                                1, (255,255,255), 2, cv2.LINE_AA)


    def __result_callback(self, result, output_image, timestamp_ms):

        self.lock.acquire() # solves potential concurrency issues
        self.current_gestures = []

        if result is not None and any(result.gestures):

            for single_hand_gesture_data in result.gestures:
                gesture_name = single_hand_gesture_data[0].category_name

                self.current_gestures.append(gesture_name)

                if gesture_name == self.gesture_to_do:
                    self.points += 1

                    if self.random_mode == True:
                        self.gesture_to_do = random.choice(gestures)
                    else:
                        if self.gesture_to_do == "Closed_Fist":
                            self.gesture_to_do = "Open_Palm"
                        else:
                            self.gesture_to_do = "Closed_Fist"


        self.lock.release()

def main():
    """ Main function. """

    parser = argparse.ArgumentParser()
    parser.add_argument("-r", "--random_mode", action="store_true",
                        help="If flag used, gives user randomly allocated gestures.")

    args = parser.parse_args()

    threading.Thread(target=playsound, args=('space.mp3',), daemon=True).start()
    # playsound('space.mp3')

    rec = HelpingHandGame()
    if args.random_mode:
        rec.random_mode = True
    else:
        rec.random_mode = False

    rec.main()

if __name__ == "__main__":
    main()

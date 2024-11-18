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

MODEL_PATH = os.path.join("model", "gesture_recognizer.task")
GESTURES = ["Pointing_Up", "Closed_Fist", "Open_Palm", 
            "ILoveYou", "Victory", "Thumb_Up", "Thumb_Down"]
READABLE_GESTURES = {"Pointing_Up": "Point finger", "Closed_Fist": "closed fist",
                    "Open_Palm": "Open hand", "ILoveYou": "I love you",
                    "Victory": "Peace sign", "Thumb_Up": "Thumbs up", 
                    "Thumb_Down": "Thumbs down"}


def preload_images():
    """ Load gesture images and masks in advance. """

    images = {}
    masks = {}

    for gesture in GESTURES:
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

    astronaut_with_bg = cv2.resize(astro_image, (300, 400))

    # Create a mask
    _, astro_mask = cv2.threshold(astronaut_with_bg, 1, 255, cv2.THRESH_BINARY)

    # Apply the mask
    astronaut = cv2.bitwise_and(astronaut_with_bg, astro_mask)

    return astronaut, cv2.bitwise_not(astro_mask)


class HelpingHandGame():
    """ Game, recognising hand gestures. """

    def __init__(self, random_mode):
        """ Main game function. """

        # Preload graphics
        self.images, self.masks = preload_images()
        self.masked_astronaut, self.astro_mask = load_astronaut()

        # Set game mode
        self.random_mode = random_mode

        # Initialise point score
        self.points = 0

        # Setup gesture recognition system
        self.lock = threading.Lock()
        options = mp.tasks.vision.GestureRecognizerOptions(
            base_options=python.BaseOptions(model_asset_path=MODEL_PATH),
            running_mode=mp.tasks.vision.RunningMode.LIVE_STREAM,
            num_hands = 1,
            result_callback=self.__result_callback)
        self.recognizer = mp.tasks.vision.GestureRecognizer.create_from_options(options)

        self.run_game()


    def run_game(self):
        """ Run the rehabilitation game. """
        timestamp = 0
        mp_drawing = mp.solutions.drawing_utils
        mp_hands = mp.solutions.hands
        hands = mp_hands.Hands(
                static_image_mode=False,
                max_num_hands=1,
                min_detection_confidence=0.65,
                min_tracking_confidence=0.65)

        # Set initial goal gesture
        if self.random_mode is True:
            self.gesture_to_do = random.choice(GESTURES)
        else:
            self.gesture_to_do = "Closed_Fist"

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
                    self.recognizer.recognize_async(mp_image, timestamp)
                    timestamp += 1

                self.display_goal_gesture(frame)

            cv2.imshow("A Helping Hand", frame)
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
        cv2.putText(frame, "Goal gesture: " + READABLE_GESTURES[goal_gesture],
                    (10, 50), cv2.FONT_HERSHEY_SIMPLEX,
                    1, (255,255,255), 2, cv2.LINE_AA)

        # Display the goal gesture as an image
        curr_fr = cv2.bitwise_and(frame[100:400, 50:350], cv2.bitwise_not(self.masks[goal_gesture]))
        logo = cv2.bitwise_and(self.images[goal_gesture], self.masks[goal_gesture])
        roi = cv2.bitwise_or(curr_fr, logo)

        frame[100:400, 50:350] = roi

        # Display the astronaut
        curr_fr = cv2.bitwise_and(frame[600:1000, 1500:1800], self.astro_mask)
        roi = cv2.bitwise_or(curr_fr, self.masked_astronaut)
        frame[600:1000, 1500:1800] = roi

        # Display the user's score
        cv2.rectangle(frame, (5, 410), (200, 475), (102,47,32), -1)
        cv2.putText(frame, "Score: " + str(user_score), (13, 450), cv2.FONT_HERSHEY_SIMPLEX,
                                1, (255,255,255), 2, cv2.LINE_AA)


    def __result_callback(self, result, output_image, timestamp_ms):
        """ Function triggered when gesture recognised. """

        self.lock.acquire() # solves potential concurrency issues

        if result is not None and any(result.gestures):

            for single_hand_gesture_data in result.gestures:
                gesture_name = single_hand_gesture_data[0].category_name

                if gesture_name == self.gesture_to_do:
                    self.points += 1

                    if self.random_mode is True:
                        self.gesture_to_do = random.choice(GESTURES)
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

    rec = HelpingHandGame(args.random_mode)

if __name__ == "__main__":
    main()

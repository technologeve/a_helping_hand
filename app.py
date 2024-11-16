
import random
from second import GestureRecognizer

gestures = ["Pointing_Up", "Closed_Fist", "Open_Palm", "ILoveYou", "Victory"]


if __name__ == "__main__":
    gesture_to_do = random.choice(gestures)
    print(gesture_to_do)
    
    
    # rec = GestureRecognizer()
    # rec.main()

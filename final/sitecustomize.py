import sys


# Block cv2 import everywhere
sys.modules["cv2"] = None

import os
import sys

# Disable Docling heavy parts
os.environ["DOCLING_DISABLE_TABLE_MODEL"] = "1"
os.environ["DOCLING_DISABLE_LAYOUT_MODEL"] = "1"
os.environ["DOCLING_DISABLE_OCR"] = "1"
os.environ["DOCLING_CPU_ONLY"] = "1"
os.environ["CUDA_VISIBLE_DEVICES"] = ""

# Block cv2 import everywhere
sys.modules["cv2"] = None

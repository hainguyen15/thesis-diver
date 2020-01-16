import os
import cv2
import numpy as np


def get_boundary(binary_mask):
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9,9))
    dilated = cv2.dilate(binary_mask, kernel, iterations=3)
    _, contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for item in contours:
        yield item.reshape(-1, 2).tolist()

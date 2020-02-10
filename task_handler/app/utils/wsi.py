import cv2


def get_boundary(binary_mask):
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9,9))
    dilated = cv2.dilate(binary_mask, kernel, iterations=3)
    _, contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    # res = []
    for item in contours:
        item = item * 16
        # res.append(item.reshape(-1, 2).tolist())
        yield item.reshape(-1, 2).tolist()
    # return res

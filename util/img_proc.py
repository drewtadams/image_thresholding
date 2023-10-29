from typing import List, Tuple, Union
import cv2
import numpy as np


CLOSE = 0
OPEN = 1


def apply_clahe(img: np.ndarray, clip_limit: float = 2.0, title_grid_size: Tuple[int, int] = (8, 8)):
    """
    applies CLAHE to each image in [imgs] and returns the updated list
    :param img: image to apply CLAHE
    :param clip_limit: contrast limiting threshold value
    :param title_grid_size: grid size for the equalization grid
    :return: updated image
    """
    return cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=title_grid_size).apply(img)


def apply_img_mask(
        mask_color: Union[int, Tuple],
        imgs: List,
        min_foreground_area: int = 10000000,
        max_foreground_area: int = 13000000,
        threshold: int = 75):
    """
    in-place operation that fills the inverse foreground contour for each passed image
    :param mask_color: (R, G, B) color or L luminance of the contour fill
    :param imgs: list of images
    :param min_foreground_area: minimum px area of the foreground in the image
    :param max_foreground_area: maximum px area of the foreground in the image
    :param threshold: minimum px threshold for black and white conversion
    :return: None
    """
    for i, img in enumerate(imgs):
        # convert the image to prep for closure
        proc_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if len(img.shape) > 2 else img  # grayscale
        proc_img = cv2.GaussianBlur(proc_img, (3, 3), 0)  # gaussian blur
        _, proc_img = cv2.threshold(proc_img, threshold, 255, cv2.THRESH_BINARY)  # black and white

        # apply open -> close to remove noise then fill line gaps
        proc_img = open_close(proc_img, OPEN, 10)
        proc_img = open_close(proc_img, CLOSE, 10)

        #
        cur_min_contour = tuple()
        contours = cv2.findContours(proc_img, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)[-2]
        for contour in contours:
            # outline should only be within the range of the area for the piece of paper
            if min_foreground_area < (contour_area := cv2.contourArea(contour)) < max_foreground_area:
                if not cur_min_contour or (cur_min_contour and cur_min_contour[1] > contour_area):
                    mask_val = 255
                    stencil_shape = img.shape[:2]

                    # get the bounding box
                    rect = cv2.minAreaRect(contour)
                    box = cv2.boxPoints(rect)
                    box = np.int0(box)

                    # fill everything BUT the bounding box
                    stencil = np.zeros(stencil_shape).astype(np.uint8)
                    cv2.fillPoly(stencil, [box], mask_val)
                    inverse_mask = stencil != mask_val
                    img[inverse_mask] = mask_color

                    # keep track of the current smallest contour
                    cur_min_contour = (contour, contour_area)

        # update by reference
        imgs[i] = img


def open_close(img: np.ndarray, proc_enum: int, open_close_iterations: int = 5) -> np.ndarray:
    """
    applies the open or close process on a copy of the passed image and returns the results
    :param img: image to have opening/closing processing done
    :param proc_enum: precess enum belonging to the desired process (CLOSE or OPEN)
    :param open_close_iterations: number of erosion/dilation iterations
    :return: np.ndarray image
    """
    proc_funcs = [cv2.dilate, cv2.erode]
    img_copy = img.copy()

    # primary function call (dilate or erode)
    img_copy = proc_funcs[proc_enum](img_copy, None, iterations=open_close_iterations)

    # secondary function call (erode or dilate)
    img_copy = proc_funcs[(proc_enum + 1) % len(proc_funcs)](img_copy, None, iterations=open_close_iterations)

    return img_copy

from PIL import Image, ImageTk
from tkinter import ttk
from util import img_proc
import cv2
import numpy as np
import tkinter as tk


highlighted_img = cv2.imread('images/20190723_183846_highlighted.jpg')
og_img = cv2.imread('images/20190723_183846_original.jpg')
resize_size = (800, 1067)
thresh_bin = cv2.THRESH_BINARY

default_max = 255
default_thresh = 65
num_open_close_iter = 3

# apply background mask
black_mask = (0, 0, 0)
white_mask = (255, 255, 255)
img_proc.apply_img_mask(white_mask, [og_img, highlighted_img])


def get_bw_img() -> np.ndarray:
    # get threshold and max values and threshold strategy
    bwv_val = int(bw_thresh_val.get())
    bwm_val = int(bw_thresh_max.get())
    thresh_strategy = thresh_bin | cv2.THRESH_OTSU if int(is_otsu.get()) else thresh_bin

    # apply the threshold to the og image
    gray_img = cv2.cvtColor(og_img, cv2.COLOR_BGR2GRAY)

    # apply CLAHE
    clahe_img = img_proc.apply_clahe(gray_img)
    bw_bin_img = cv2.threshold(clahe_img, bwv_val, bwm_val, thresh_strategy)[1]

    # apply open morph to remove noise
    bw_bin_img = cv2.GaussianBlur(bw_bin_img, (3, 3), 0)
    bw_bin_img = img_proc.open_close(bw_bin_img, img_proc.CLOSE, num_open_close_iter)

    # convert images to 3 channel
    og_counted = cv2.cvtColor(highlighted_img, cv2.COLOR_BGR2RGB)
    bw_bin_img = cv2.cvtColor(bw_bin_img, cv2.COLOR_GRAY2RGB)

    # resize and regenerate the side-by-side images
    og_counted = cv2.resize(og_counted, resize_size)
    bw_bin_img = cv2.resize(bw_bin_img, resize_size)
    return np.concatenate((og_counted, bw_bin_img), axis=1)


def get_rgb_img() -> np.ndarray:
    # get the threshold and max values
    rv_val = int(red_thresh_val.get())
    rm_val = int(red_thresh_max.get())
    gv_val = int(green_thresh_val.get())
    gm_val = int(green_thresh_max.get())
    bv_val = int(blue_thresh_val.get())
    bm_val = int(blue_thresh_max.get())

    # apply the threshold to the og image
    _, r_bin_red = cv2.threshold(og_img[:, :, 2], rv_val, rm_val, thresh_bin)
    _, r_bin_green = cv2.threshold(og_img[:, :, 1], gv_val, gm_val, thresh_bin)
    _, r_bin_blue = cv2.threshold(og_img[:, :, 0], bv_val, bm_val, thresh_bin)

    # apply close morph to remove noise
    rgb_bin_img = cv2.cvtColor(cv2.merge((r_bin_blue, r_bin_green, r_bin_red)), cv2.COLOR_BGR2RGB)
    rgb_bin_img = cv2.GaussianBlur(rgb_bin_img, (3, 3), 0)
    rgb_bin_img = img_proc.open_close(rgb_bin_img, img_proc.CLOSE, num_open_close_iter)

    # regenerate the side-by-side images
    og_counted = cv2.resize(cv2.cvtColor(highlighted_img, cv2.COLOR_BGR2RGB), resize_size)
    r_bin_img = cv2.resize(rgb_bin_img, resize_size)
    return np.concatenate((og_counted, r_bin_img), axis=1)


def refresh_img():
    refreshed_img = get_bw_img() if int(is_bw.get()) else get_rgb_img()

    # recreate the image widget
    r_img_tk = ImageTk.PhotoImage(image=Image.fromarray(refreshed_img))

    # update the label
    primary_img.config(image=r_img_tk)
    primary_img.image = r_img_tk


def show_bw_ctrl():
    rgb_thresh_frame.grid_forget()
    bw_thresh_frame.grid(row=1, column=37, columnspan=6)


def show_rgb_ctrl():
    bw_thresh_frame.grid_forget()
    rgb_thresh_frame.grid(row=1, column=37, columnspan=6)


root = tk.Tk()
root.title('image thresholding')

# threshold input fields
validate_input = root.register(lambda action, field, value, reason, **kwargs: len(value) <= 3)

# bw frame
bw_thresh_frame = tk.Frame(root)
bw_thresh_val = ttk.Entry(bw_thresh_frame, width=3, validate="key", validatecommand=(validate_input, '%d', '%W', '%P', '%v'))
bw_thresh_max = ttk.Entry(bw_thresh_frame, width=3, validate="key", validatecommand=(validate_input, '%d', '%W', '%P', '%v'))
bw_thresh_val.insert(default_thresh, str(default_thresh))
bw_thresh_max.insert(default_max, str(default_max))
is_otsu = tk.StringVar()
is_otsu.set(0)

# rgb frame
rgb_thresh_frame = tk.Frame(root)
red_thresh_val = ttk.Entry(rgb_thresh_frame, width=3, validate="key", validatecommand=(validate_input, '%d', '%W', '%P', '%v'))
red_thresh_max = ttk.Entry(rgb_thresh_frame, width=3, validate="key", validatecommand=(validate_input, '%d', '%W', '%P', '%v'))
red_thresh_val.insert(default_thresh, str(default_thresh))
red_thresh_max.insert(default_max, str(default_max))
green_thresh_val = ttk.Entry(rgb_thresh_frame, width=3, validate="key", validatecommand=(validate_input, '%d', '%W', '%P', '%v'))
green_thresh_max = ttk.Entry(rgb_thresh_frame, width=3, validate="key", validatecommand=(validate_input, '%d', '%W', '%P', '%v'))
green_thresh_val.insert(default_thresh, str(default_thresh))
green_thresh_max.insert(default_max, str(default_max))
blue_thresh_val = ttk.Entry(rgb_thresh_frame, width=3, validate="key", validatecommand=(validate_input, '%d', '%W', '%P', '%v'))
blue_thresh_max = ttk.Entry(rgb_thresh_frame, width=3, validate="key", validatecommand=(validate_input, '%d', '%W', '%P', '%v'))
blue_thresh_val.insert(default_thresh, str(default_thresh))
blue_thresh_max.insert(default_max, str(default_max))

# load the image
img_tk = ImageTk.PhotoImage(image=Image.fromarray(get_bw_img()))
primary_img = ttk.Label(root, image=img_tk)
primary_img.grid(row=0, column=0, columnspan=80)

# bw frame layout
ttk.Label(bw_thresh_frame, text='black & white (val | max):').grid(row=0, column=0)
bw_thresh_val.grid(row=0, column=1)
ttk.Label(bw_thresh_frame, text='|').grid(row=0, column=2)
bw_thresh_max.grid(row=0, column=3)
ttk.Radiobutton(bw_thresh_frame, text='standard', variable=is_otsu, value=0).grid(row=1, column=0)
ttk.Radiobutton(bw_thresh_frame, text='OTSU', variable=is_otsu, value=1).grid(row=1, column=1)

# rgb frame layout
ttk.Label(rgb_thresh_frame, text='red (val | max):').grid(row=0, column=0)
red_thresh_val.grid(row=0, column=1)
ttk.Label(rgb_thresh_frame, text='|').grid(row=0, column=2)
red_thresh_max.grid(row=0, column=3)
ttk.Label(rgb_thresh_frame, text='green (val | max):').grid(row=1, column=0)
green_thresh_val.grid(row=1, column=1)
ttk.Label(rgb_thresh_frame, text='|').grid(row=1, column=2)
green_thresh_max.grid(row=1, column=3)
ttk.Label(rgb_thresh_frame, text='blue (val | max):').grid(row=2, column=0)
blue_thresh_val.grid(row=2, column=1)
ttk.Label(rgb_thresh_frame, text='|').grid(row=2, column=2)
blue_thresh_max.grid(row=2, column=3)

show_bw_ctrl()

# rgb/bw toggle
is_bw = tk.StringVar()
is_bw.set(1)
ttk.Radiobutton(root, text='RGB', variable=is_bw, value=0, command=show_rgb_ctrl).grid(row=3, column=39)
ttk.Radiobutton(root, text='B/W', variable=is_bw, value=1, command=show_bw_ctrl).grid(row=3, column=40)

# refresh button
ttk.Button(root, text='refresh', command=refresh_img).grid(row=4, column=39)

# start tkinter
root.mainloop()

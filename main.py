from PIL import Image, ImageTk
from tkinter import ttk
from util.img_proc import apply_img_mask
import cv2
import numpy as np
import tkinter as tk


resize_size = (800, 1067)
og_img = cv2.imread('images/20190723_183846_original.jpg')
highlighted_img = cv2.imread('images/20190723_183846_highlighted.jpg')
thresh_bin = cv2.THRESH_BINARY

# apply background mask
apply_img_mask((0, 0, 0), [og_img, highlighted_img])


def get_bw_img() -> np.ndarray:
    # get threshold and max value
    bwv_val = int(bw_thresh_val.get())
    bwm_val = int(bw_thresh_max.get())

    # apply the threshold to the og image
    gray_img = cv2.cvtColor(og_img, cv2.COLOR_BGR2GRAY)
    bin_img = cv2.threshold(gray_img, bwv_val, bwm_val, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]

    # regenerate the side-by-side images
    og_counted = cv2.resize(cv2.cvtColor(highlighted_img, cv2.COLOR_BGR2RGB), resize_size)
    r_bin_img = cv2.resize(cv2.cvtColor(bin_img, cv2.COLOR_GRAY2RGB), resize_size)
    return np.concatenate((og_counted, r_bin_img), axis=1)


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

    # regenerate the side-by-side images
    og_counted = cv2.resize(cv2.cvtColor(highlighted_img, cv2.COLOR_BGR2RGB), resize_size)
    r_bin_img = cv2.resize(cv2.cvtColor(cv2.merge((r_bin_blue, r_bin_green, r_bin_red)), cv2.COLOR_BGR2RGB), resize_size)
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
bw_thresh_val.insert(65, '65')
bw_thresh_max.insert(255, '255')

# rgb frame
rgb_thresh_frame = tk.Frame(root)
red_thresh_val = ttk.Entry(rgb_thresh_frame, width=3, validate="key", validatecommand=(validate_input, '%d', '%W', '%P', '%v'))
red_thresh_max = ttk.Entry(rgb_thresh_frame, width=3, validate="key", validatecommand=(validate_input, '%d', '%W', '%P', '%v'))
red_thresh_val.insert(65, '65')
red_thresh_max.insert(255, '255')
green_thresh_val = ttk.Entry(rgb_thresh_frame, width=3, validate="key", validatecommand=(validate_input, '%d', '%W', '%P', '%v'))
green_thresh_max = ttk.Entry(rgb_thresh_frame, width=3, validate="key", validatecommand=(validate_input, '%d', '%W', '%P', '%v'))
green_thresh_val.insert(65, '65')
green_thresh_max.insert(255, '255')
blue_thresh_val = ttk.Entry(rgb_thresh_frame, width=3, validate="key", validatecommand=(validate_input, '%d', '%W', '%P', '%v'))
blue_thresh_max = ttk.Entry(rgb_thresh_frame, width=3, validate="key", validatecommand=(validate_input, '%d', '%W', '%P', '%v'))
blue_thresh_val.insert(65, '65')
blue_thresh_max.insert(255, '255')

# apply the threshold to the og image
_, bin_red = cv2.threshold(og_img[:, :, 2], 65, 255, thresh_bin)
_, bin_green = cv2.threshold(og_img[:, :, 1], 65, 255, thresh_bin)
_, bin_blue = cv2.threshold(og_img[:, :, 0], 65, 255, thresh_bin)

# convert images from BGR to RGB and concatenate them
highlighted_img_rgb = cv2.resize(cv2.cvtColor(highlighted_img, cv2.COLOR_BGR2RGB), resize_size)
bin_img = cv2.resize(cv2.cvtColor(cv2.merge((bin_blue, bin_green, bin_red)), cv2.COLOR_BGR2RGB), resize_size)
h_concat = np.concatenate((highlighted_img_rgb, bin_img), axis=1)

# load the image
img_tk = ImageTk.PhotoImage(image=Image.fromarray(h_concat))
primary_img = ttk.Label(root, image=img_tk)
primary_img.grid(row=0, column=0, columnspan=80)

# bw frame layout
ttk.Label(bw_thresh_frame, text='BLACK & WHITE (val | max):').grid(row=0, column=0)
bw_thresh_val.grid(row=0, column=1)
ttk.Label(bw_thresh_frame, text='|').grid(row=0, column=2)
bw_thresh_max.grid(row=0, column=3)

# rgb frame layout
ttk.Label(rgb_thresh_frame, text='RED (val | max):').grid(row=0, column=0)
red_thresh_val.grid(row=0, column=1)
ttk.Label(rgb_thresh_frame, text='|').grid(row=0, column=2)
red_thresh_max.grid(row=0, column=3)
ttk.Label(rgb_thresh_frame, text='GREEN (val | max):').grid(row=1, column=0)
green_thresh_val.grid(row=1, column=1)
ttk.Label(rgb_thresh_frame, text='|').grid(row=1, column=2)
green_thresh_max.grid(row=1, column=3)
ttk.Label(rgb_thresh_frame, text='BLUE (val | max):').grid(row=2, column=0)
blue_thresh_val.grid(row=2, column=1)
ttk.Label(rgb_thresh_frame, text='|').grid(row=2, column=2)
blue_thresh_max.grid(row=2, column=3)

show_rgb_ctrl()

# rgb/bw toggle
is_bw = tk.StringVar()
is_bw.set(0)
ttk.Radiobutton(root, text='RGB', variable=is_bw, value=0, command=show_rgb_ctrl).grid(row=3, column=39)
ttk.Radiobutton(root, text='B/W', variable=is_bw, value=1, command=show_bw_ctrl).grid(row=3, column=40)

# refresh button
ttk.Button(root, text='refresh', command=refresh_img).grid(row=4, column=39)

# start tkinter
root.mainloop()

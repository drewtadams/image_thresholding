from PIL import Image, ImageTk
from tkinter import ttk
import cv2
import numpy as np
import tkinter as tk


resize_size = (800, 1067)
og_img = cv2.imread('images/20190723_183846_original.jpg')
highlighted_img = cv2.imread('images/20190723_183846_highlighted.jpg')


def refresh_img():
    # get the threshold values
    rl_val = int(red_thresh_low_val.get())
    rh_val = int(red_thresh_high_val.get())
    gl_val = int(green_thresh_low_val.get())
    gh_val = int(green_thresh_high_val.get())
    bl_val = int(blue_thresh_low_val.get())
    bh_val = int(blue_thresh_high_val.get())

    # apply the threshold to the og image
    _, r_bin_red = cv2.threshold(og_img[:, :, 2], rl_val, rh_val, cv2.THRESH_BINARY_INV)
    _, r_bin_green = cv2.threshold(og_img[:, :, 1], gl_val, gh_val, cv2.THRESH_BINARY_INV)
    _, r_bin_blue = cv2.threshold(og_img[:, :, 0], bl_val, bh_val, cv2.THRESH_BINARY_INV)

    # regenerate the side-by-side images
    og_counted = cv2.resize(cv2.cvtColor(highlighted_img, cv2.COLOR_BGR2RGB), resize_size)
    r_bin_img = cv2.resize(cv2.cvtColor(cv2.merge((r_bin_blue, r_bin_green, r_bin_red)), cv2.COLOR_BGR2RGB), resize_size)
    r_h_concat = np.concatenate((og_counted, r_bin_img), axis=1)

    # recreate the image widget
    r_img_tk = ImageTk.PhotoImage(image=Image.fromarray(r_h_concat))
    # label = ttk.Label(root, image=img_tk)

    # update the label
    label.config(image=r_img_tk)
    label.image = r_img_tk


root = tk.Tk()
root.title('image thresholding')

# threshold input fields
validate_input = root.register(lambda action, field, value, reason, **kwargs: len(value) <= 3)
red_thresh_low_val = ttk.Entry(root, width=3, validate="key", validatecommand=(validate_input, '%d', '%W', '%P', '%v'))
red_thresh_high_val = ttk.Entry(root, width=3, validate="key", validatecommand=(validate_input, '%d', '%W', '%P', '%v'))
red_thresh_low_val.insert(128, '128')
red_thresh_high_val.insert(255, '255')
green_thresh_low_val = ttk.Entry(root, width=3, validate="key", validatecommand=(validate_input, '%d', '%W', '%P', '%v'))
green_thresh_high_val = ttk.Entry(root, width=3, validate="key", validatecommand=(validate_input, '%d', '%W', '%P', '%v'))
green_thresh_low_val.insert(128, '128')
green_thresh_high_val.insert(255, '255')
blue_thresh_low_val = ttk.Entry(root, width=3, validate="key", validatecommand=(validate_input, '%d', '%W', '%P', '%v'))
blue_thresh_high_val = ttk.Entry(root, width=3, validate="key", validatecommand=(validate_input, '%d', '%W', '%P', '%v'))
blue_thresh_low_val.insert(128, '128')
blue_thresh_high_val.insert(255, '255')

# refresh button
refresh_btn = ttk.Button(root, text='refresh', command=refresh_img)

# apply the threshold to the og image
_, bin_red = cv2.threshold(og_img[:, :, 2], 128, 255, cv2.THRESH_BINARY_INV)
_, bin_green = cv2.threshold(og_img[:, :, 1], 128, 255, cv2.THRESH_BINARY_INV)
_, bin_blue = cv2.threshold(og_img[:, :, 0], 128, 255, cv2.THRESH_BINARY_INV)

# convert images from BGR to RGB and concatenate them
highlighted_img_rgb = cv2.resize(cv2.cvtColor(highlighted_img, cv2.COLOR_BGR2RGB), resize_size)
bin_img = cv2.resize(cv2.cvtColor(cv2.merge((bin_blue, bin_green, bin_red)), cv2.COLOR_BGR2RGB), resize_size)
h_concat = np.concatenate((highlighted_img_rgb, bin_img), axis=1)

# load the image
img_tk = ImageTk.PhotoImage(image=Image.fromarray(h_concat))
label = ttk.Label(root, image=img_tk)

# widget layout
label.grid(row=0, column=0, columnspan=80)

ttk.Label(root, text='RED (low | high):').grid(row=1, column=39)
red_thresh_low_val.grid(row=1, column=40)
ttk.Label(root, text='|').grid(row=1, column=41)
red_thresh_high_val.grid(row=1, column=42)

ttk.Label(root, text='GREEN (low | high):').grid(row=2, column=39)
green_thresh_low_val.grid(row=2, column=40)
ttk.Label(root, text='|').grid(row=2, column=41)
green_thresh_high_val.grid(row=2, column=42)

ttk.Label(root, text='BLUE (low | high):').grid(row=3, column=39)
blue_thresh_low_val.grid(row=3, column=40)
ttk.Label(root, text='|').grid(row=3, column=41)
blue_thresh_high_val.grid(row=3, column=42)

refresh_btn.grid(row=4, column=40)

# start tkinter
root.mainloop()

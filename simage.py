import time
import tkinter as tk
from PIL import Image, ImageTk
import win32gui
import win32con
import threading

root = None
canvas = None
tk_image = None

dwWidth = None
dwHeight = None

def init(width, height):  # Simage 1.0.4
    global root, canvas, dwWidth, dwHeight

    dwWidth = width
    dwHeight = height

    root = tk.Tk()
    root.attributes('-topmost', True)
    root.geometry(f'{width}x{height}')
    root.overrideredirect(True)
    root.attributes('-transparentcolor', 'black')
    root.config(bg='black')

    canvas = tk.Canvas(root, width=width, height=height, bg='black', highlightthickness=0)
    canvas.pack()

    root.update()

    root.after(256, touchlessWindow)

def touchlessWindow():
    hwnd = win32gui.FindWindow(None, root.winfo_toplevel().title())
    extended_style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
    win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE,
                           extended_style | win32con.WS_EX_LAYERED | win32con.WS_EX_TRANSPARENT)

def show(image_path, position='center', duration=1000, sizex=100, sizey=100, x=0, y=0):
    global tk_image

    # Load and resize the image
    image = Image.open(image_path)
    image = image.resize((sizex, sizey), Image.Resampling.LANCZOS)

    tk_image = ImageTk.PhotoImage(image)

    if position == 'center':
        x_pos = dwWidth // 2 + x
        y_pos = dwHeight // 2 + y
    elif position == 'top':
        x_pos = dwWidth // 2 + x
        y_pos = 0 + y
    elif position == 'bottom':
        x_pos = dwWidth // 2 + x
        y_pos = dwHeight + y
    elif position == 'left':
        x_pos = 0 + x
        y_pos = dwHeight // 2 + y
    elif position == 'right':
        x_pos = dwWidth + x
        y_pos = dwHeight // 2 + y
    else:
        print('sImage Error 2: Not existing value.\n'
              ' Please, choose one of: "center", "top", "bottom", "left" or "right"')

    # Create the image on the canvas
    image_on_canvas = canvas.create_image(x_pos, y_pos, image=tk_image)
    root.update()  # Show the image

    # Schedule the hide function to run after 'duration' milliseconds
    root.after(duration, lambda: hide(image_on_canvas))

def hide(image_on_canvas):
    canvas.delete(image_on_canvas)
    root.update()  # Hide the image

def overlay():
    root.mainloop()  # Overlay apply
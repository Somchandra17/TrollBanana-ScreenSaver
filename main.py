import tkinter as tk
from tkinter import PhotoImage, Canvas
import ctypes
import random
import platform
import os
import subprocess

def get_mouse_position():
    if platform.system() == "Linux":
        try:
            output = subprocess.check_output(['xdotool', 'getmouselocation']).decode()
            x = int(output.split()[0].split(':')[1])
            y = int(output.split()[1].split(':')[1])
            return (x, y)
        except:
            root = tk.Tk()
            x = root.winfo_pointerx()
            y = root.winfo_pointery()
            root.destroy()
            return (x, y)
    else:
        import pyautogui
        return pyautogui.position()

class Banana:
    def __init__(self, scene, x=0, y=0):
        self.scene = scene
        try:
            self.image = PhotoImage(file='banana1.png')
            self.image = self.image.subsample(16)
            self.image_bomb = PhotoImage(file='bomb.png')
            self.image_bomb = self.image_bomb.subsample(8)
        except tk.TclError:
            print("Error: Could not load image files. Make sure 'banana1.png' and 'bomb.png' exist in the current directory.")
            return
            
        self.imageRef = scene.canvas.create_image(x, y, image=self.image)
        self.bomb_status = False

    def update(self):
        x, y = get_mouse_position()
        ban_x, ban_y = self.scene.canvas.coords(self.imageRef)
        dist = (abs(x-ban_x) + abs(y-ban_y))

        if self.bomb_status:
            self.scene.canvas.move(
                self.imageRef,
                random.choice((-30, 30)),
                random.choice((-30, 30))
            )
            self.scene.canvas.itemconfig(self.imageRef, image=self.image)
            for _ in range(10):
                self.scene.new_banana(
                    random.randint(0, self.scene.screen_width),
                    random.randint(0, self.scene.screen_height)
                )
            self.bomb_status = False
        elif dist < 5:
            self.scene.canvas.itemconfig(self.imageRef, image=self.image_bomb)
            self.bomb_status = True
        else:
            numero = random.choice((1, 2, 5))
            self.scene.canvas.move(
                self.imageRef,
                numero if x > ban_x else -numero,
                numero if y > ban_y else -numero
            )

class Scene:
    def __init__(self, window: tk.Tk):
        self.screen_width = window.winfo_screenwidth()
        self.screen_height = window.winfo_screenheight()
        self.canvas = Canvas(
            window,
            width=self.screen_width,
            height=self.screen_height,
            highlightthickness=0,
            bg='white'
        )
        self.canvas.pack()
        self.bananas = []

    def update(self):
        for banana in self.bananas:
            banana.update()

    def new_banana(self, x, y):
        banana = Banana(self)
        self.canvas.move(banana.imageRef, x, y)
        self.bananas.append(banana)

class Game:
    def __init__(self):
        self.window = self.create_window()
        if platform.system() == "Windows":
            self.apply_click_through(self.window)
        self.scene = Scene(self.window)

    def update(self):
        try:
            self.scene.update()
            self.window.after(5, self.update)
        except tk.TclError:
            print("Window was closed")
            return

    def create_window(self):
        window = tk.Tk()
        window.wm_attributes("-topmost", True)
        window.attributes("-fullscreen", True)
        window.overrideredirect(True)
        
        # Handle transparency based on OS
        if platform.system() == "Windows":
            window.attributes('-transparentcolor', 'white')
        elif platform.system() == "Linux":
            window.attributes('-alpha', 0.8)  # Set window transparency
            window.wait_visibility(window)
        
        window.config(bg='white')
        
        # Add key binding to close the window
        window.bind('<Escape>', lambda e: window.destroy())
        
        return window

    def apply_click_through(self, window):
        WS_EX_TRANSPARENT = 0x00000020
        WS_EX_LAYERED = 0x00080000
        GWL_EXSTYLE = -20
        
        hwnd = ctypes.windll.user32.GetParent(window.winfo_id())
        style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
        style = style | WS_EX_TRANSPARENT | WS_EX_LAYERED
        ctypes.windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, style)

    def start(self):
        self.update()
        self.window.mainloop()

if __name__ == "__main__":
    try:
        if platform.system() == "Linux":
            try:
                subprocess.check_output(['which', 'xdotool'])
            except subprocess.CalledProcessError:
                print("Please install xdotool: sudo apt-get install xdotool")
                exit(1)
        
        game = Game()
        game.scene.new_banana(100, 100)
        game.start()
    except Exception as e:
        print(f"An error occurred: {e}")

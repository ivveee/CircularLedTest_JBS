import tkinter as tk
from tkinter import ttk
import asyncio


class App:
    async def exec(self):
        self.window = Window(asyncio.get_event_loop())
        await self.window.show()


class Window(tk.Tk):
    def __init__(self, loop):
        self.loop = loop
        self.root = tk.Tk()
        self.root.geometry('1200x500')
        # self.animation = "░▒▒▒▒▒"
        # self.label = tk.Label(text="")
        # button_non_block.grid(row=2, column=1, sticky=tk.W, padx=8, pady=8)
        self.canvas = tk.Canvas(self.root,width=1200, height=500)
        self.canvas.pack()
        self.create_circle(100, 100, 10, self.rgbtohex(255, 255, 255))
        self.circles = {}

    def rgbtohex(self, r, g, b):
        return f'#{r:02x}{g:02x}{b:02x}'

    def create_circle(self, x, y, r, fill:str):  # center coordinates, radius
        x0 = x - r
        y0 = y - r
        x1 = x + r
        y1 = y + r
        return self.canvas.create_oval(x0, y0, x1, y1, fill=fill)

    async def show(self):
        while True:
            # self.label["text"] = self.animation
            # self.animation = self.animation[1:] + self.animation[0]
            self.root.update()
            await asyncio.sleep(.1)

    async def calculate_async(self):
        max = 3000000
        for i in range(1, max):
            self.progressbar["value"] = i / max * 100
            if i % 1000 == 0:
                await asyncio.sleep(0)

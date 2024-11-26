import os
import tkinter as tk

root = tk.Tk()
root.title("Simple Tkinter App")
root.geometry("400x300")  # Set the size of the window to 400x300 pixels

button = tk.Button(root, text="Click Me")
button.pack()

root.mainloop()
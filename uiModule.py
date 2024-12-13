import os
import sys
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
from io import BytesIO
import threading
import re

from speechModule import SpeechModule
from LLMModule import LLMModule
from pictureModule import PictureModule

class RecipeApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Recipe Suggestion App")
        self.geometry("600x800")

        # Instances of your modules
        self.speech_module = SpeechModule()
        self.llm_module = LLMModule()
        self.picture_module = PictureModule()

        # Data
        self.recipes_with_pictures = []
        self.current_recipe_index = 0
        self.is_recording = False  # Track if recording is active

        explanation_text = (
            "How to use:\n"
            "1. Press the button to start recording and describe the items in your fridge.\n"
            "2. Press the button again to stop recording.\n"
            "3. Explore the suggested recipes once they are displayed."
        )
        self.intro_label = tk.Label(self, text=explanation_text, wraplength=500, justify='left')
        self.intro_label.pack(pady=10)

        # Single toggle button for recording
        self.record_button = tk.Button(self, text="Start Recording", command=self.toggle_recording)
        self.record_button.pack(pady=5)

        # Label that will show "Waiting for results..."
        self.waiting_label = tk.Label(self, text="", font=("Helvetica", 14))

        self.recipe_frame = tk.Frame(self)
        self.recipe_title_label = tk.Label(self.recipe_frame, text="", font=("Helvetica", 16))
        self.recipe_time_label = tk.Label(self.recipe_frame, text="", font=("Helvetica", 12))

        # Image label
        self.recipe_image_label = tk.Label(self.recipe_frame)

        # Buttons frame for recipe navigation
        self.buttons_frame = tk.Frame(self.recipe_frame)
        self.show_steps_button = tk.Button(self.buttons_frame, text="Show Recipe Steps", command=self.show_recipe_steps)
        self.different_button = tk.Button(self.buttons_frame, text="I Want Something Different", command=self.next_recipe)

        self.recipe_steps_label = tk.Label(self.recipe_frame, text="", wraplength=500, justify="left")

        # Quit button (initially hidden)
        self.quit_button = tk.Button(self, text="Quit Application", command=self.quit)

        # Label to show when no more recipes are available
        self.no_more_label = tk.Label(self, text="", font=("Helvetica", 14))

        # Restart button at the bottom
        self.restart_button = tk.Button(self, text="Restart", command=self.restart_application)
        self.restart_button.pack(side=tk.BOTTOM, pady=5)

    def restart_application(self):
        """Restart the entire application."""
        python = sys.executable
        os.execl(python, python, *sys.argv)

    def toggle_recording(self):
        if not self.is_recording:
            self.start_recording()
        else:
            self.stop_recording()

    def start_recording(self):
        self.is_recording = True
        self.speech_module.start_recording()
        self.record_button.config(text="Stop Recording")
        print("Recording started...")

    def stop_recording(self):
        self.is_recording = False
        self.intro_label.pack_forget()
        self.record_button.pack_forget()

        self.waiting_label.config(text="Waiting for results...")
        self.waiting_label.pack(pady=20)

        def stop_and_recognize():
            self.speech_module.stop_recording()
            print("Recording stopped, now recognizing audio...")
            recognized_text = self.speech_module.recognize_audio()
            self.after(0, lambda: self.process_recognized_text(recognized_text))

        threading.Thread(target=stop_and_recognize, daemon=True).start()

    def process_recognized_text(self, text):
        self.waiting_label.pack_forget()
        # Do not show the record button again
        print("get_recipe_suggestions")
        recipes = self.llm_module.get_recipe_suggestions(text)
        print(recipes)
        print("create_picture")
        self.recipes_with_pictures = self.picture_module.create_picture(recipes)

        if not self.recipes_with_pictures:
            self.no_more_label.config(text="No recipes could be suggested.")
            self.no_more_label.pack(pady=20)
            self.quit_button.pack(pady=5)
            return

        self.current_recipe_index = 0
        self.show_recipe(self.current_recipe_index)

    def show_recipe(self, index):
        for widget in self.recipe_frame.winfo_children():
            widget.pack_forget()

        self.recipe_frame.pack(pady=10)
        recipe = self.recipes_with_pictures[index]

        self.recipe_title_label.config(text=recipe["recipeTitle"])
        self.recipe_time_label.config(text=f"Time Estimate: {recipe['timeEstimate']}")
        self.recipe_title_label.pack(pady=10)
        self.recipe_time_label.pack()

        self.no_more_label.pack_forget()
        self.quit_button.pack_forget()
        self.recipe_steps_label.config(text="")
        self.recipe_steps_label.pack_forget()

        self.recipe_image_label.pack_forget()
        self.buttons_frame.pack_forget()

        self.update_idletasks()

        def load_and_resize_image():
            image_data = recipe["picture"].getvalue()
            pil_image = Image.open(BytesIO(image_data))
            pil_image = pil_image.resize((300, 300), Image.LANCZOS)
            self.recipe_image = ImageTk.PhotoImage(pil_image)
            self.after(0, self._show_image_and_buttons)

        threading.Thread(target=load_and_resize_image, daemon=True).start()

    def _show_image_and_buttons(self):
        self.recipe_image_label.config(image=self.recipe_image)
        self.recipe_image_label.pack(pady=10)

        self.show_steps_button.pack(side=tk.LEFT, padx=5)
        self.different_button.pack(side=tk.LEFT, padx=5)
        self.buttons_frame.pack(pady=10)
        self.update_idletasks()

    def show_recipe_steps(self):
        recipe = self.recipes_with_pictures[self.current_recipe_index]
        original_steps = recipe["recipeSteps"]
        final_steps = f"Steps:\n{original_steps}"
        self.recipe_steps_label.config(text=final_steps)

        self.show_steps_button.pack_forget()
        self.different_button.pack_forget()
        self.recipe_steps_label.pack(pady=10)
        self.quit_button.pack(pady=5)

    def next_recipe(self):
        self.current_recipe_index += 1
        if self.current_recipe_index < len(self.recipes_with_pictures):
            self.show_recipe(self.current_recipe_index)
        else:
            self.recipe_frame.pack_forget()
            self.no_more_label.config(text="No more recipes available.")
            self.no_more_label.pack(pady=20)
            self.quit_button.pack(pady=5)

if __name__ == "__main__":
    app = RecipeApp()
    app.mainloop()

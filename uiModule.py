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
        self.animating_loading_gif = False  # Flag to control GIF animation

        explanation_text = (
            "How to use:\n"
            "1. Press the button to start recording and describe the items in your fridge.\n"
            "2. Press the button again to stop recording.\n"
            "3. Navigate through the suggested recipes using the arrows."
        )
        self.intro_label = tk.Label(self, text=explanation_text, wraplength=500, justify='left')
        self.intro_label.pack(pady=10)

        # Single toggle button for recording
        self.record_button = tk.Button(self, text="Start Recording", command=self.toggle_recording)
        self.record_button.pack(pady=5)

        # Loading GIF display
        # Ensure you have a GIF file named 'video.gif' in the same directory
        # If the GIF has multiple frames, load them all
        self.loading_frames = []
        try:
            i = 0
            while True:
                # Attempt to load each frame of the gif
                frame = tk.PhotoImage(file='video.gif', format=f'gif -index {i}')
                self.loading_frames.append(frame)
                i += 1
        except Exception as e:
            print(f"Error loading GIF frames: {e}")

        self.loading_gif_label = tk.Label(self)

        self.recipe_frame = tk.Frame(self)
        self.recipe_frame.pack(pady=10)  # Keep the recipe frame centered

        self.recipe_title_label = tk.Label(self.recipe_frame, text="", font=("Helvetica", 16))
        self.recipe_time_label = tk.Label(self.recipe_frame, text="", font=("Helvetica", 12))

        self.image_navigation_frame = tk.Frame(self.recipe_frame)

        # Always display arrows
        self.left_arrow_button = tk.Button(self.image_navigation_frame, text="←", command=self.prev_recipe)
        self.right_arrow_button = tk.Button(self.image_navigation_frame, text="→", command=self.next_recipe)
        self.recipe_image_label = tk.Label(self.image_navigation_frame)

        # Configure columns to keep image centered
        self.image_navigation_frame.grid_columnconfigure(0, weight=1)
        self.image_navigation_frame.grid_columnconfigure(1, weight=0)
        self.image_navigation_frame.grid_columnconfigure(2, weight=1)

        self.recipe_steps_label = tk.Label(self.recipe_frame, text="", wraplength=500, justify="left")

        # Quit button (initially hidden)
        self.quit_button = tk.Button(self, text="Quit Application", command=self.quit)

        # Label to show when no more recipes are available
        self.no_more_label = tk.Label(self, text="", font=("Helvetica", 14))

        # Restart button at the bottom
        self.restart_button = tk.Button(self, text="Restart", command=self.restart_application)
        self.restart_button.pack(side=tk.BOTTOM, pady=5)

        self.current_loading_frame = 0

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

        # Show loading animation instead of "Waiting for results..."
        self.show_loading_gif()

        def stop_and_recognize():
            self.speech_module.stop_recording()
            print("Recording stopped, now recognizing audio...")
            recognized_text = self.speech_module.recognize_audio()
            # Start a new thread to process recipes to avoid blocking the main thread
            threading.Thread(target=self.process_recognized_text, args=(recognized_text,), daemon=True).start()

        threading.Thread(target=stop_and_recognize, daemon=True).start()

    def show_loading_gif(self):
        """Show the animated GIF while waiting for LLM results."""
        if self.loading_frames:
            self.animating_loading_gif = True  # Start animation
            self.loading_gif_label.pack(pady=20)
            self.animate_gif()
        else:
            # If no frames are loaded, show a simple waiting text
            self.loading_gif_label.config(text="Waiting for results...")
            self.loading_gif_label.pack(pady=20)

    def animate_gif(self):
        """Cycle through the frames of the GIF."""
        if self.animating_loading_gif and self.loading_frames:
            try:
                frame = self.loading_frames[self.current_loading_frame]
                self.loading_gif_label.config(image=frame)
                self.current_loading_frame = (self.current_loading_frame + 1) % len(self.loading_frames)
                self.after(100, self.animate_gif)  # adjust delay as needed
            except Exception as e:
                print(f"Error during GIF animation: {e}")
                self.animating_loading_gif = False  # Stop animation on error

    def process_recognized_text(self, text):
        """
        This method runs in a separate thread to prevent blocking the main thread.
        It processes the recognized text to fetch recipes and generate pictures.
        Once done, it updates the GUI using thread-safe methods.
        """
        print("get_recipe_suggestions")
        recipes = self.llm_module.get_recipe_suggestions(text)
        print(recipes)
        print("create_picture")
        recipes_with_pictures = self.picture_module.create_picture(recipes)

        # Now, update the GUI on the main thread
        self.after(0, lambda: self.update_gui_with_recipes(recipes_with_pictures))

    def update_gui_with_recipes(self, recipes_with_pictures):
        """Update the GUI with the fetched recipes and stop the loading animation."""
        # Stop the GIF animation
        self.animating_loading_gif = False
        self.loading_gif_label.pack_forget()

        self.recipes_with_pictures = recipes_with_pictures

        if not self.recipes_with_pictures:
            self.no_more_label.config(text="No recipes could be suggested.")
            self.no_more_label.pack(pady=20)
            self.quit_button.pack(pady=5)
            return

        self.current_recipe_index = 0
        self.show_recipe(self.current_recipe_index)

    def show_recipe(self, index):
        # Clear previous widgets
        for widget in self.recipe_frame.winfo_children():
            widget.pack_forget()

        recipe = self.recipes_with_pictures[index]

        self.recipe_title_label.config(text=recipe["recipeTitle"])
        self.recipe_title_label.pack(pady=10)

        self.recipe_time_label.config(text=f"Time Estimate: {recipe['timeEstimate']}")
        self.recipe_time_label.pack()

        self.no_more_label.pack_forget()
        self.quit_button.pack_forget()

        self.recipe_steps_label.config(text="")
        self.recipe_steps_label.pack_forget()

        # Clear image navigation frame content from previous state
        for widget in self.image_navigation_frame.winfo_children():
            widget.grid_forget()

        self.image_navigation_frame.pack_forget()

        self.update_idletasks()

        # Check if picture is available
        if recipe["picture"] is None:
            # No picture, show placeholder text immediately
            self._show_no_picture_and_steps()
        else:
            # If picture is available, load and display it
            def load_and_resize_image():
                try:
                    image_data = recipe["picture"].getvalue()
                    pil_image = Image.open(BytesIO(image_data))
                    pil_image = pil_image.resize((300, 300), Image.LANCZOS)
                    self.recipe_image = ImageTk.PhotoImage(pil_image)
                    self.after(0, self._show_image_and_steps)
                except Exception as e:
                    print(f"Error loading recipe image: {e}")
                    self.after(0, self._show_no_picture_and_steps)

            threading.Thread(target=load_and_resize_image, daemon=True).start()

    def _show_no_picture_and_steps(self):
        # Determine if buttons should be enabled or disabled
        if self.current_recipe_index > 0:
            self.left_arrow_button.config(state="normal")
        else:
            self.left_arrow_button.config(state="disabled")

        if self.current_recipe_index < len(self.recipes_with_pictures) - 1:
            self.right_arrow_button.config(state="normal")
        else:
            self.right_arrow_button.config(state="disabled")

        # Display "Could not generate picture"
        no_picture_label = tk.Label(self.image_navigation_frame, text="Could not generate picture")

        self.left_arrow_button.grid(row=0, column=0, padx=5, sticky="e")
        no_picture_label.grid(row=0, column=1, padx=5)
        self.right_arrow_button.grid(row=0, column=2, padx=5, sticky="w")

        self.image_navigation_frame.pack(pady=10, fill='x')

        # Show steps by default
        recipe = self.recipes_with_pictures[self.current_recipe_index]
        final_steps = f"Steps:\n{recipe['recipeSteps']}"
        self.recipe_steps_label.config(text=final_steps)
        self.recipe_steps_label.pack(pady=10)

        self.quit_button.pack(pady=5)
        self.update_idletasks()

    def _show_image_and_steps(self):
        # Determine if buttons should be enabled or disabled
        if self.current_recipe_index > 0:
            self.left_arrow_button.config(state="normal")
        else:
            self.left_arrow_button.config(state="disabled")

        if self.current_recipe_index < len(self.recipes_with_pictures) - 1:
            self.right_arrow_button.config(state="normal")
        else:
            self.right_arrow_button.config(state="disabled")

        # Place arrows and image
        self.left_arrow_button.grid(row=0, column=0, padx=5, sticky="e")
        self.recipe_image_label.config(image=self.recipe_image)
        self.recipe_image_label.grid(row=0, column=1, padx=5)
        self.right_arrow_button.grid(row=0, column=2, padx=5, sticky="w")

        self.image_navigation_frame.pack(pady=10, fill='x')

        # Show steps by default
        recipe = self.recipes_with_pictures[self.current_recipe_index]
        final_steps = f"Steps:\n{recipe['recipeSteps']}"
        self.recipe_steps_label.config(text=final_steps)
        self.recipe_steps_label.pack(pady=10)

        self.quit_button.pack(pady=5)
        self.update_idletasks()

    def prev_recipe(self):
        if self.current_recipe_index > 0:
            self.current_recipe_index -= 1
            self.show_recipe(self.current_recipe_index)

    def next_recipe(self):
        self.current_recipe_index += 1
        if self.current_recipe_index < len(self.recipes_with_pictures):
            self.show_recipe(self.current_recipe_index)
        else:
            for widget in self.recipe_frame.winfo_children():
                widget.pack_forget()
            self.no_more_label.config(text="No more recipes available.")
            self.no_more_label.pack(pady=20)
            self.quit_button.pack(pady=5)

if __name__ == "__main__":
    app = RecipeApp()
    app.mainloop()

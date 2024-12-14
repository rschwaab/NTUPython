# import requests

# # Recipe data
# recipe_prompt = "A delicious plate of scrambled eggs with toast, perfectly cooked and served on a cozy breakfast table, with a glass of orange juice and a napkin nearby. Bright and appetizing."

# # API endpoint
# url = f"https://image.pollinations.ai/prompt/{recipe_prompt}"

# # Send request to generate image
# response = requests.get(url)

# # Save image locally
# if response.status_code == 200:
#     with open("scrambled_eggs_with_toast.jpg", "wb") as file:
#         file.write(response.content)
#     print("Image saved as scrambled_eggs_with_toast.jpg")
# else:
#     print(f"Failed to generate image: {response.status_code}")


# class PictureModule:
    
#     # Function to create picture of recipes
#     def create_picture(self, recipes):
#         # Send the request to pollinations
#         # figure out how to send the requests in parallel
#         recipes_with_pictures = {}
#         for recipe in recipes:
#             recipe_prompt = recipe["recipeTitle"]
#             url = f"https://image.pollinations.ai/prompt/{recipe_prompt}"
#             response = requests.get(url)
#             if response.status_code == 200:
#                 recipe["picture"] = response.content
#                 recipes_with_pictures.append(recipe)

import requests
from concurrent.futures import ThreadPoolExecutor
import base64
from io import BytesIO

class PictureModule:

    def create_picture(self, recipes):
        """
        Add pictures to each recipe by fetching them from Pollinations API and storing them as base64.

        Parameters:
            recipes (list of dict): A list of recipe dictionaries in JSON format.

        Returns:
            list of dict: A list of recipe dictionaries with pictures added as base64 strings.
        """

        def fetch_picture(recipe):
            """Fetch the picture for a single recipe."""
            recipe_prompt = recipe.get("recipeTitle")
            url = f"https://image.pollinations.ai/prompt/{recipe_prompt}"
            response = requests.get(url)
            if response.status_code == 200:
                # Store the image as base64
                recipe["picture"] = BytesIO(response.content)
            else:
                recipe["picture"] = None  # Handle failed image generation
            return recipe

        # Use ThreadPoolExecutor to send requests in parallel
        with ThreadPoolExecutor() as executor:
            recipes_with_pictures = list(executor.map(fetch_picture, recipes))

        return recipes_with_pictures


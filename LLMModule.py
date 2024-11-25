import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
genai.configure(api_key=GEMINI_API_KEY)

class LLMModule:
    
    # Function to send ingredients to the Gemini API and retrieve recipes
    def get_recipe_suggestions(self, input_text):

        # Define the prompt to send to the API
        prompt = f"""You are an agent for an app that takes input from users that want to get recipes based on the food they have left in their fridge. This is the voice input from the user: "{input_text}"
        Provide recipes for these ingredients in the following JSON format:
        [{{"recipeTitle": "...", "recipeSteps": "..."}}]
        """

        # Send the request to the Gemini API
        try:
            model = genai.GenerativeModel("gemini-1.5-flash")
            response = model.generate_content(prompt)
            print(response.text)
            recipes = response.json()

            return recipes
        except:
            return 0

if __name__ == "__main__":
    example = LLMModule()
    response = example.get_recipe_suggestions("I have apples, flour, eggs adn sugar.")
    print(response)
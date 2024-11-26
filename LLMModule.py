import os
from dotenv import load_dotenv
import google.generativeai as genai
import json

load_dotenv()

# Get your own API key from https://aistudio.google.com/app/apikey
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
genai.configure(api_key=GEMINI_API_KEY)

class LLMModule:
    
    # Function to send ingredients to the Gemini API and retrieve recipes
    def get_recipe_suggestions(self, input_text):

        # Define the prompt to send to the API
        prompt = f"""You are an agent for an app that takes input from users that want to get recipes based on the food they have left in their fridge. This is the voice input from the user: "{input_text}"
        ### Instructions:
        - Only return a JSON array of recipes.
        - Do not include any text, explanations, or markdown formatting.
        - Always return three recepies.
        - The JSON array must follow this structure exactly:
        [
        {{
            "recipeTitle": "<title>",
            "recipeDescription": "<description>",
            "recipeSteps": "<steps>",
            "timeEstimate": "<time>",
        }}
        ]
        """

        # Send the request to the Gemini API
        try:
            model = genai.GenerativeModel("gemini-1.5-flash")
            response = model.generate_content(prompt)
            response_text = response.text.strip()
            if response_text.startswith("```json") and response_text.endswith("```"):
                response_text = response_text[7:-3].strip()  # Remove ```json and ```

            # Parse the response as JSON directly
            recipes = json.loads(response_text)
            return recipes
        except:
            return 0

if __name__ == "__main__":
    example = LLMModule()
    response = example.get_recipe_suggestions("I have apples, flour, eggs and sugar.")
    print(response)
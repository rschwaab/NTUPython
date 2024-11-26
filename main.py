from speechModule import SpeechModule
from llmModule import LLMModule
import json

def main():
    speech_module = SpeechModule()
    result = speech_module.listen_and_recognize()
    print("Speech recognition result: ", result)

    # TODO If the user is not satisfied with text, re run let them talk again and hopefully it goes better this time
    
    llm_module = LLMModule()
    recipes = llm_module.get_recipe_suggestions(result)
    print("Recipes: ", json.dumps(recipes, indent=4))

    # TODO Re run if the user is not happy with the receipies given

if __name__ == "__main__":
    main()
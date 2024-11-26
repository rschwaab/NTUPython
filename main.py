from speechModule import SpeechModule
from llmModule import LLMModule
import json

def main():
    speech_module = SpeechModule()
    result = speech_module.listen_and_recognize()
    print("Speech recognition result: ", result)
    
    llm_module = LLMModule()
    recipes = llm_module.get_recipe_suggestions(result)
    print("Recipes: ", json.dumps(recipes, indent=4))

if __name__ == "__main__":
    main()
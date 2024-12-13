from speechModule import SpeechModule
from LLMModule import LLMModule
from pictureModule import PictureModule
import json
from PIL import Image
import os
import base64
from io import BytesIO
from PIL import Image

def main():
    speech_module = SpeechModule()
    result = speech_module.listen_and_recognize()

    # TODO If the user is not satisfied with text, re run let them talk again and hopefully it goes better this time
    
    llm_module = LLMModule()
    recipes = llm_module.get_recipe_suggestions(result)
    picture_module = PictureModule()
    recipes_with_pictures = picture_module.create_picture(recipes)
    print(recipes_with_pictures)




if __name__ == "__main__":
    main()
from PIL import Image
from transformers import BlipProcessor, BlipForConditionalGeneration
from pathlib import Path
import google.generativeai as genai
from fastapi import APIRouter, File, UploadFile
from utils.response import response
import shutil
import re
from dotenv import load_dotenv
import os

router = APIRouter()

# Define the folder where the file will be stored
UPLOAD_FOLDER = Path("uploaded_files")
UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)

# Load the .env file
load_dotenv()

processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-large")
model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-large")

@router.post("/caption_generator")
def caption_generator_api(img_url: UploadFile = File(...)):
    try:
            # Define the path where the file will be saved
        file_path = UPLOAD_FOLDER / img_url.filename
        
        # Save the uploaded file to the specified folder
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(img_url.file, buffer)

        # Return the path or a success message

        # Image To Text Generate
        raw_image = Image.open(file_path).convert('RGB')
        inputs = processor(raw_image, return_tensors="pt")

        out = model.generate(**inputs,max_new_tokens=200)
        generated_text = processor.decode(out[0], skip_special_tokens=True)
        print("generated_text >>",generated_text)

        # Text To Caption Generate
        # Configure the API key
        genai.configure(api_key=os.getenv("GENAI_API_KEY"))

        # Set up the generation configuration
        # generation_config_feedback = {
        #     "temperature": 0.3,
        #     "top_p": 0.95,
        #     "top_k": 1,
        #     "max_output_tokens": 8192,
        # }

        model_for_feedback = genai.GenerativeModel('gemini-1.0-pro')

        prompt_feedback = f"generate 10 creative caption with emojis and relative popular hashtags from below sentence {generated_text}"

        generate_caption = model_for_feedback.generate_content(prompt_feedback).text
        # Split the string based on the numbers at the beginning of each sentence
        caption_list = re.split(r'\d+\.', generate_caption)

        # Clean up the list to remove empty strings
        caption_list = [caption.strip() for caption in caption_list if caption.strip()]
        print("generate_caption: ",caption_list)

        return response(1001,data=caption_list)
    except Exception as e:
        return response(1005)


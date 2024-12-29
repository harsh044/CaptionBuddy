from transformers import BlipProcessor, BlipForConditionalGeneration
import google.generativeai as genai
from fastapi import APIRouter, File, UploadFile
from utils.response import response
import shutil
import re
from dotenv import load_dotenv
import os
import boto3
from PIL import Image
from io import BytesIO
import requests
from pathlib import Path

router = APIRouter()

# UPLOAD_FOLDER = Path("uploaded_files")
# UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)
# Load environment variables from .env file
load_dotenv()

# Initialize AWS S3 client using boto3
s3_client = boto3.client(
    "s3",
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name="ap-south-1",  # Use your AWS region
)

BUCKET_NAME = "captionbuddy"

# Initialize BLIP processor and model for image captioning
processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-large")
model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-large")

# Function to upload image to S3 and return the file URL
async def upload_image_to_s3(img_url: UploadFile):
    try:
        # Define the path where the file will be saved temporarily
        file_path = Path("/tmp") / img_url.filename
        
        # Save the uploaded file to the specified folder
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(img_url.file, buffer)

        # Upload the file to S3
        s3_client.upload_file(
            str(file_path), 
            BUCKET_NAME, 
            img_url.filename,
        )

        # Construct the public URL for the uploaded file
        file_url = f"https://{BUCKET_NAME}.s3.{s3_client.meta.region_name}.amazonaws.com/{img_url.filename}"

        # Return the public URL
        return file_url
    except Exception as e:
        raise Exception(f"Error uploading image to S3: {str(e)}")

# Function to generate captions from the image
def generate_caption_from_image(file_path: str):
    try:
        
        # Fetch the image from the URL
        response = requests.get(file_path)
        response.raise_for_status()  # Ensure the request was successful

        # Open the image from the response content
        raw_image  = Image.open(BytesIO(response.content)).convert('RGB')
        
        # Preprocess the image
        inputs = processor(raw_image , return_tensors="pt")
        out = model.generate(**inputs, max_new_tokens=200)
        generated_text = processor.decode(out[0], skip_special_tokens=True)
        return generated_text

    except Exception as e:
        raise Exception(f"Error generating caption from image: {str(e)}")

# Function to generate creative captions using GenAI
def generate_creative_captions(generated_text: str):
    try:
        # Configure the API key for GenAI
        genai.configure(api_key=os.getenv("GENAI_API_KEY"))

        model_for_feedback = genai.GenerativeModel('gemini-1.0-pro')

        prompt_feedback = f"Generate 10 creative captions with emojis and relevant popular hashtags from the following sentence: {generated_text}"

        generate_caption = model_for_feedback.generate_content(prompt_feedback).text

        # Split the string based on the numbers at the beginning of each sentence
        caption_list = re.split(r'\d+\.', generate_caption)

        # Clean up the list to remove empty strings
        caption_list = [caption.strip() for caption in caption_list if caption.strip()]
        return caption_list
    except Exception as e:
        raise Exception(f"Error generating creative captions: {str(e)}")

@router.post("/caption_generator")
async def caption_generator_api(img_url: UploadFile = File(...)):
    try:
        # Step 1: Upload image to S3 and get the file URL
        file_url = await upload_image_to_s3(img_url)
        print(f"Image uploaded successfully to S3. File URL: {file_url}")

        # Step 2: Generate caption from the image
        generated_text = generate_caption_from_image(file_url)
        print(f"Generated text from image: {generated_text}")

        # Step 3: Generate creative captions using GenAI
        caption_list = generate_creative_captions(generated_text)
        print(f"Generated captions: {caption_list}")

        # Return the generated captions as a response
        return response(1001, data=caption_list)

    except Exception as e:
        print(f"Error in caption_generator_api: {str(e)}")
        return response(1005)

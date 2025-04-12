from typing import Union, Dict
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import shutil
import os
import base64
from tempfile import NamedTemporaryFile
from face_recog import find_faces
import re
import io
from PIL import Image

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ImageData(BaseModel):
    frame: str

def decode_base64_image(base64_string: str) -> bytes:
    """
    Decode base64 image data and return bytes
    """
    # Remove the data URL prefix if present
    if 'data:image' in base64_string:
        base64_string = base64_string.split('base64,')[1]
    
    try:
        # Decode base64 string
        image_bytes = base64.b64decode(base64_string)
        return image_bytes
    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid base64 image data")

@app.post("/recognize-face-base64")
async def recognize_face_base64(image_data: ImageData):
    """
    Endpoint to recognize faces in a base64 encoded image.
    Accepts base64 image data and returns recognition results.
    """
    try:
        # Decode base64 image
        image_bytes = decode_base64_image(image_data.frame)
        
        # Create a temporary file to store the decoded image
        with NamedTemporaryFile(suffix='.jpg', delete=False) as temp_file:
            temp_file.write(image_bytes)
            temp_path = temp_file.name
        
        try:
            # Process the image with face recognition
            results = find_faces(temp_path)
            
            # Clean up the temporary file
            os.unlink(temp_path)
            
            return {
                "status": "success",
                "faces_found": len(results),
                "results": results
            }
            
        except Exception as e:
            # Clean up the temporary file in case of error
            if os.path.exists(temp_path):
                os.unlink(temp_path)
            raise HTTPException(status_code=500, detail=str(e))
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/recognize-face")
async def recognize_face(file: UploadFile = File(...)):
    """
    Endpoint to recognize faces in an uploaded image.
    Accepts an image file and returns recognition results.
    """
    try:
        # Validate file type
        if not file.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Create a temporary file to store the uploaded image
        with NamedTemporaryFile(delete=False) as temp_file:
            shutil.copyfileobj(file.file, temp_file)
            temp_path = temp_file.name
        
        try:
            # Process the image with face recognition
            results = find_faces(temp_path)
            
            # Clean up the temporary file
            os.unlink(temp_path)
            
            return {
                "status": "success",
                "faces_found": len(results),
                "results": results
            }
            
        except Exception as e:
            # Clean up the temporary file in case of error
            if os.path.exists(temp_path):
                os.unlink(temp_path)
            raise HTTPException(status_code=500, detail=str(e))
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        file.file.close()

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}
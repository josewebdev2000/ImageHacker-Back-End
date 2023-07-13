# Back-End Server of the ImageHacker Web Application
from requests import get
from base64 import b64decode, b64encode
from uuid import uuid4
from io import BytesIO
from os import remove
from PIL import Image
from flask import Flask, request, jsonify, Response
from flask_cors import CORS

from image_editors.helpers.file_handling import get_new_image_filename
from image_editors.ImageFilterer import ImageFilterer
from image_editors.ImageBgRemover import ImageBgRemover
from image_editors.ImageConverter import ImageConverter
from image_editors.ImageCropper import ImageCropper
from image_editors.ImagePositionModifier import ImagePositionModifier
from image_editors.ImageResizer import ImageResizer

app = Flask(__name__)
CORS(app)

@app.route("/", methods=["GET"])
def home():
    """Prove to the Front-End this web server works."""
    
    message = {"message": "Web App is running"}
    return jsonify(message)

@app.route("/img-proxy", methods=["GET"])
def image_proxy():
    """Proxy an Image URL to avoid CORS Error in the Front-End."""
    
    # Get Image Url
    image_url = request.args.get("url")
    
    if image_url:
        try:
            # Receive Image from Image URL
            response = get(image_url)
            if response.status_code == 200:
                
                # Prepare headers to send to the front-end
                headers = {"Content-Type": response.headers.get("Content-Type")}
                
                # Return a response that contains image data to the front-end
                return Response(response.content, headers=headers)
        
        # If something went wrong print it
        except Exception as e:
            print(e)
    
    # Return a Not Found response in case something went wrong
    return Response(status=404)

@app.route("/edit-img", methods=["POST"])
def edit_img():
    """Get an image to apply a color filter to it."""
    
    # Read the JSON data using the request Object from Flask
    image_data = request.json
    
    # Build response message
    res = {}
    
    # Get the Base64 Encoded Image data from the request
    image_base64 = image_data["imageBase64URL"]
    
    # Get the file format from the request
    image_format = image_data["imageFormat"]
    
    # Generate a unique filename for this image
    unique_filename = str(uuid4())
        
    # Generate a unique file name to save in the temp folder
    complete_temp_filename = get_new_image_filename(
        "temp",
        unique_filename,
        image_format
        )
    
    # Decode base64 encoded Image Url
    try:
        decoded_image_data = b64decode(image_base64)
        
        # Generate a fill-like object using the decoded image data
        image_pseudo_file = BytesIO(decoded_image_data)
    
        # Generate an image object from the received image data
        image = Image.open(image_pseudo_file)
        
        # Save the image in the temp folver
        image.save(complete_temp_filename)
        
        # Close the image
        image.close()
        
        # Reopen the image saved in temp to ensure it's the right file format
        image_to_modify = Image.open(complete_temp_filename)
        
        # Apply filter to the image
        editted_image = ImageFilterer.transform_to_black_n_white(image_to_modify)
        
        # Create a stream to get image binary data
        stream_for_editted_image = BytesIO()
        
        # Save the editted image to the temp folder with the format of the editted image
        editted_image.save(stream_for_editted_image, format=editted_image.format)
        
        # Seek back the beginning of the stream
        stream_for_editted_image.seek(0)
        
        # Read the stream to get the image data as bytes
        image_bytes = stream_for_editted_image.read()
        
        # Encode the bytes in base64
        encoded_image_data = b64encode(image_bytes).decode("utf-8")
        
        # Add the image data to the response
        res["imageBase64URL"] = encoded_image_data
        
        # Add the image format to the response as well
        res["imageFormat"] = editted_image.format.lower()
        
        # Close the editted image object
        editted_image.close()
        
        return jsonify(res)
    
    except Exception as e:
        raise e
    
    finally:
         # Remove the image since it's no longer required
        remove(complete_temp_filename)
    
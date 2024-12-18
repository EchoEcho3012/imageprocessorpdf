from flask import Flask, request, jsonify
import cv2
from PIL import Image, ImageEnhance
import os

app = Flask(__name__)

@app.route("/process", methods=["POST"])
def process_image():
    try:
        # Get input and output paths from the request
        input_url = request.json["input_url"]
        output_filename = request.json["output_filename"]

        # Download the image from the input URL
        temp_input_path = "input_image.png"
        import requests

        # Download the image
        response = requests.get(input_url)
        if response.status_code == 200:
            with open(temp_input_path, "wb") as file:
                file.write(response.content)
            print("Image downloaded successfully.")
        else:
            print(f"Failed to download image. Status code: {response.status_code}")
            return jsonify({"error": "Failed to download image."}), 400
        
        if not os.path.exists(temp_input_path) or os.path.getsize(temp_input_path) == 0:
            print("Downloaded file is empty or missing.")
            return jsonify({"error": "Downloaded file is empty or missing."}), 400


        # Load and process the image
        image = cv2.imread(temp_input_path)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        temp_processed_path = "temp_processed.png"
        cv2.imwrite(temp_processed_path, thresh)

        # Enhance using Pillow
        img = Image.open(temp_processed_path)
        img = ImageEnhance.Sharpness(img).enhance(2.0)
        img = ImageEnhance.Contrast(img).enhance(1.5)
        output_path = f"{output_filename}.pdf"
        img.convert('RGB').save(output_path, "PDF")

        return jsonify({"message": "Image processed successfully", "output_file": output_path})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)

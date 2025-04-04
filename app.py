import os
from PIL import Image
from dotenv import load_dotenv
import google.generativeai as genai
from flask import Flask, request, render_template

# Load environment variables from .env
load_dotenv()

# Configure Google Generative AI
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Load models
vis_model = genai.GenerativeModel('gemini-2.0-flash')  # Vision model
text_model = genai.GenerativeModel('gemini-2.0-flash')  # Text model

app = Flask(__name__)

# Function to generate medical content from an image
def gen_image(prompt, image):
    response = vis_model.generate_content([image])  # Pass as list
    return response.text if hasattr(response, 'text') else "Error in processing image."

# Function to validate medical context
def validate(validation_prompt):
    vresponse = text_model.generate_content(validation_prompt)
    return vresponse.text.strip().lower()  # Normalize response

# Route for the main page
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        image_prompt = '''
        - Generate a very detailed medical description for the given image.
        - Identify and describe any relevant medical conditions, anomalies, or abnormalities present in the image.
        - Additionally, provide insights into any potential treatments or recommended actions based on the observed medical features.
        - Ensure the generated content is accurate and clinically relevant.
        - Do not provide false or misleading information.
        '''
        
        uploaded_file = request.files.get('file')  # Get uploaded file safely
        if not uploaded_file:
            return render_template('index.html', response_text="No file uploaded.")

        try:
            image = Image.open(uploaded_file)
            response_text = gen_image(image_prompt, image)
        except Exception as e:
            return render_template('index.html', response_text=f"Error processing image: {str(e)}")

        validation_prompt = "Check if the provided context is related to the medical field. Just reply with 'Yes' or 'No'."
        vans = validate(validation_prompt)

        if "yes" in vans:
            return render_template('index.html', response_text=response_text)
        else:
            return render_template('index.html', response_text="Please provide a valid medical image.")

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)

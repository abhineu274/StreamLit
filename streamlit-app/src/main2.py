import streamlit as st
from openai import AzureOpenAI
import os
from dotenv import load_dotenv
import requests
import base64
from io import BytesIO
import json

# Load environment variables
load_dotenv()

endpoint = os.getenv("ENDPOINT_URL", "https://aoai-d01.openai.azure.com/")
image_deployment = os.getenv("DALL_E_DEPLOYMENT_NAME", "dall-e-3")

client = AzureOpenAI(
    azure_endpoint=endpoint,
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version="2024-05-01-preview",
)

# Function to generate images using DALL·E
def generate_image(prompt):
    try:
        response = client.images.generate(
            model=image_deployment,
            prompt=prompt,
            n=1,
            size="1024x1024"
        )
        image_url = json.loads(response.model_dump_json())['data'][0]['url']  # Get image URL
        return image_url
    except openai.error.BadRequestError as e:
        st.error(f"Failed to generate image: {e}")
        return None

# Streamlit UI
st.title("DALL-E Image Generator")

with st.form(key="image_form"):
    prompt = st.text_input("Enter Image Prompt")
    submit_button = st.form_submit_button(label="Generate Image")

if submit_button:
    if prompt:
        image_url = generate_image(prompt)
        if image_url:
            st.image(image_url, caption="Generated Image", use_column_width=True)
            # Provide download link
            img_response = requests.get(image_url)
            img_stream = BytesIO(img_response.content)
            b64 = base64.b64encode(img_stream.getvalue()).decode()
            href = f'<a href="data:file/png;base64,{b64}" download="generated_image.png">Download Image</a>'
            st.markdown(href, unsafe_allow_html=True)
    else:
        st.warning("Please enter an image prompt.")
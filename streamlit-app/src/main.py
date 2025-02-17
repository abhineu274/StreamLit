import streamlit as st
from openai import AzureOpenAI
import os
from dotenv import load_dotenv
from pptx import Presentation
from pptx.util import Inches
import base64

# Load environment variables
load_dotenv()

endpoint = os.getenv("ENDPOINT_URL", "https://aoai-d01.openai.azure.com/")
deployment = os.getenv("DEPLOYMENT_NAME", "gpt-4o")

client = AzureOpenAI(
    azure_endpoint=endpoint,
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version="2024-05-01-preview",
)

st.title("Azure OpenAI Streamlit App")

with st.form(key='ppt_form'):
    topic = st.text_input("Enter PPT Topic")
    number_of_slides = st.number_input("Enter Number of Slides", min_value=1, step=1)
    submit_button = st.form_submit_button(label='Generate Presentation')

if submit_button:
    if topic and number_of_slides:
        chat_prompt = [
            {
                "role": "system",
                "content": [
                    {
                        "type": "text",
                        "text": f"Generate a presentation on {topic} with {number_of_slides} slides. Also create relevant DALL-E images."
                    }
                ]
            }
        ]

        messages = chat_prompt

        response = client.chat.completions.create(
            model=deployment,
            messages=messages,
            max_tokens=800,
            temperature=0.7,
            top_p=0.95,
            frequency_penalty=0,
            presence_penalty=0,
            stop=None,
            stream=False
        )
        st.write(response.choices[0].message.content)
        presentation_text = response.choices[0].message.content

        # Create a presentation
        prs = Presentation()
        slide_layout = prs.slide_layouts[1]

        for i in range(number_of_slides):
            slide = prs.slides.add_slide(slide_layout)
            title = slide.shapes.title
            content = slide.placeholders[1]
            title.text = f"Slide {i+1}"
            content.text = presentation_text

        pptx_file = "generated_presentation.pptx"
        prs.save(pptx_file)

        # Provide download link
        with open(pptx_file, "rb") as f:
            bytes_data = f.read()
            b64 = base64.b64encode(bytes_data).decode()
            href = f'<a href="data:file/pptx;base64,{b64}" download="{pptx_file}">Download Presentation</a>'
            st.markdown(href, unsafe_allow_html=True)

    else:
        st.warning("Please enter both topic and number of slides.")
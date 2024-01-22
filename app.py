# Import necessary libraries
import google.generativeai as genai
import streamlit as st
from PIL import Image
from streamlit.components.v1 import html
import re

# IF AI Feature didnt work then do not import this but directly use the list inside the code
from custom_ai import data_analyst_questions, nlp_engineer_questions, data_engineer_questions

# Configure the library with your API key
genai.configure(api_key="Your-API-Key-Here")

# Add a script to prevent data loss on page reload
alert_box = """
<script>
window.onbeforeunload = function() {
    return "Data will be lost if you leave the page, are you sure?";
}
</script>
"""

html(alert_box, height=0)

# Define safety settings for content generation
safety_settings = [
    {"category": "HARM_CATEGORY_DANGEROUS", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
]

# Sidebar layout
st.sidebar.markdown('<h1> CHATGRAPH 📊📈📉</h1>', unsafe_allow_html=True)
st.write('Documentation of ChatGraph can be found [here]()')
st.write('other Projects:\n- Create a Copilot inside your Notebook [link](https://github.com/FareedKhan-dev/create-copilot-in-your-notebooks) \n- Powerful NLP Library 2024 [link](https://github.com/FareedKhan-dev/Most-powerful-NLP-library) \n - Building Million Parameter LLM [link](https://github.com/FareedKhan-dev/create-million-parameter-llm-from-scratch)')
st.markdown("""<hr>""", unsafe_allow_html=True)
st.sidebar.write("")
st.sidebar.write("Created by Fareed Khan")
st.sidebar.write("Profiles: [Linkedin](https://www.linkedin.com/in/fareed-khan-dev/), [Medium](https://medium.com/@fareedkhandev), [GitHub](https://github.com/FareedKhan-dev)")

# Initialize user messages if not already present
if "user_messages" not in st.session_state:
    st.session_state.user_messages = ""

# Provide a download button for the user
import random
random_number = random.randint(0,100000)
st.sidebar.download_button(
    label="Export Chat",
    data=st.session_state.user_messages,
    key="download_chat",
    help="Click to download the chat conversation",
    file_name=f"chat_export_{random_number}.txt",
)

# adding hr line
st.sidebar.markdown("""<hr>""", unsafe_allow_html=True)

# Create a sidebar with the topic selection
selected_topic = st.sidebar.multiselect("Select Topics", options=["Data Analyst", "NLP", "Data Engineer"], default=["Data Analyst"], max_selections=1)

st.sidebar.markdown("""<hr>""", unsafe_allow_html=True)

# Add custom style
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@100..900&display=swap'); 

* {
    font-family: 'Inter', sans-serif; 
}
h1 {
    font-family: "Inter", sans-serif;
}
.st-emotion-cache-16txtl3.eczjsme4 {
    margin-top: -75px;
}
</style>
""", unsafe_allow_html=True)

# Initialize the GenerativeModel with 'gemini-pro' for chat and code
image_model = genai.GenerativeModel('gemini-pro-vision')

# Create a dictionary to map topics to lists
topic_lists = {
    "Data Analyst": data_analyst_questions,
    "NLP": nlp_engineer_questions,
    "Data Engineer": data_engineer_questions,
}

# Radio checkbox for prompt style selection
selected_item = st.sidebar.radio("Which style of Prompt you want to use", ['Manual', 'AI', 'Enhanced AI'])

st.sidebar.markdown("""<hr>""", unsafe_allow_html=True)

# Slider for the number of responses to display
num_responses = st.sidebar.slider("Conversation history (no. of messages)", min_value=0, max_value=30, value=30, step=10)

# Add hr line
st.sidebar.markdown("""<hr>""", unsafe_allow_html=True)

# Initialize messages and ai_generated_question in session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Initialize ai_generated_question in session state
if "ai_generated_question" not in st.session_state:
    st.session_state.ai_generated_question = {}

# New code snippet to handle image upload and selection
uploaded_images = st.sidebar.file_uploader("Upload Images", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

# Initialize selected image in session state
if "selected_image" not in st.session_state:
    st.session_state.selected_image = None

# Select image from the uploaded images
selected_image = st.sidebar.multiselect("Select Image", options=uploaded_images, format_func=lambda x: x.name if x else "None", max_selections=1)

# Display selected image in the sidebar
if selected_image:
    st.sidebar.image(selected_image, caption="Selected Image", use_column_width=True)
    st.session_state.selected_image = selected_image

# Display existing messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# Add custom style
st.markdown("""
<style>
            .stSelectbox {
            position: fixed;
            bottom: 3rem;
            }
            .st-emotion-cache-1ocxcnq {
            display: none;
            }
</style>
""", unsafe_allow_html=True)

# Load the selected image as a PIL image
image = Image.open(st.session_state.selected_image[0]) if st.session_state.selected_image else None

# Chat input based on selected prompt style
if selected_item == 'Manual':
    if st.session_state.selected_image:
        outer_prompt = st.chat_input("What is up?")
    else:
        st.write("Please select an image to use chat feature")
        outer_prompt = None
elif selected_item == 'AI':
    # Use the selected topic to get the corresponding list
    if selected_topic:
        if st.session_state.selected_image is not None:
            selected_list = topic_lists[selected_topic[0]]
            selected_list.insert(0, None)
            selected_topic = f"""The Selected Topic is **{selected_topic[0]}**"""
            init_prompt = st.selectbox(label=selected_topic,options=selected_list, placeholder='Auto complete prompt using AI')
            outer_prompt = init_prompt
        else:
            st.write("Please select an image to use AI based prompt from selected topic")
            outer_prompt = None
    else:
        selected_topic = "Please Select a Topic"
        outer_prompt = None
elif selected_item == 'Enhanced AI':
    if st.session_state.selected_image:
        generating_message = st.empty()
        if st.session_state.selected_image[0].name not in st.session_state.ai_generated_question.keys():
            generating_message.text("Generating prompts...")

            prompt = "give 20 question related to this image that a user can ask?"
            err = image_model.generate_content([image, prompt])
            questions = re.findall(r'\d+\.\s(.+)', err.text)
            st.session_state.ai_generated_question[st.session_state.selected_image[0].name] = questions
            questions.insert(0, None)
            init_prompt = st.selectbox(label="ai generated questions",options=questions, placeholder='AI Generated Prompts')
            outer_prompt = init_prompt

            generating_message.empty()
        elif st.session_state.selected_image[0].name in st.session_state.ai_generated_question.keys():
            questions = st.session_state.ai_generated_question[st.session_state.selected_image[0].name]
            init_prompt = st.selectbox(label="ai generated questions",options=questions, placeholder='AI Generated Prompts')
            outer_prompt = init_prompt
    else:
        st.write("Please select an image, AI will generate prompt for you based on the image")
        outer_prompt = None

# Chat interaction based on the selected prompt style
if (selected_item == 'Manual' and outer_prompt is not None and st.session_state.selected_image is not None) or (selected_item == 'AI' and outer_prompt is not None and st.session_state.selected_image is not None) or (selected_item == 'Enhanced AI' and outer_prompt is not None and st.session_state.selected_image is not None):

    prompt = outer_prompt

    # HTML content with smooth scroll function
    smooth_scroll_html = """
    <script>
    function smoothScroll() {
        var textAreas = parent.document.querySelectorAll('section.main');

        function scrollToBottom(element) {
            var scrollHeight = element.scrollHeight;
            var currentScrollTop = element.scrollTop;
            var targetScrollTop = scrollHeight;
            var delta = targetScrollTop - currentScrollTop;

            function scrollStep() {
                currentScrollTop = currentScrollTop + delta / 100;
                element.scrollTop = currentScrollTop;

                if (currentScrollTop < targetScrollTop) {
                    requestAnimationFrame(scrollStep);
                }
            }

            requestAnimationFrame(scrollStep);
        }

        for (let index = 0; index < textAreas.length; index++) {
            scrollToBottom(textAreas[index]);
        }
    }

    smoothScroll();
    </script>
    """

    html(smooth_scroll_html, height=0)

    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    # Include the selected image in the prompt
    prompt_with_image = f'{prompt} [image: {st.session_state.selected_image[0].name}]' if st.session_state.selected_image else prompt

    with st.chat_message("assistant"), st.spinner(""):
        st.session_state.user_messages += f"user:{prompt}, gemini_Response:"
        message_placeholder = st.empty()
        full_response = ""
        for response in image_model.generate_content([image,st.session_state.user_messages], safety_settings=safety_settings):
            full_response += (response.text or "")
            message_placeholder.markdown(full_response + "▌")
        message_placeholder.markdown(full_response)
    st.session_state.messages.append({"role": "assistant", "content": full_response})
    st.session_state.user_messages += f"{full_response}\n\n"

    if len(st.session_state.user_messages.split("\n\n")) > num_responses:
        responses = st.session_state.user_messages.split("\n\n")[-num_responses:]
        st.session_state.user_messages = "\n\n".join(responses)    
    else:
        pass

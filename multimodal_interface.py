import streamlit as st
from agno.agent import Agent
from agno.run.agent import RunOutput
from agno.media import Image, File, Video
from agno.models.google import Gemini
import tempfile
import os

def main():
    # Streamlit app title
    st.title("Multimodal Reasoning AI Agent 🧠")

    # Get Gemini API key from user in sidebar
    with st.sidebar:
        st.header("🔑 Configuration")
        gemini_api_key = st.text_input("Enter your Gemini API Key", type="password")
        st.caption(
            "Get your API key from [Google AI Studio]"
            "(https://aistudio.google.com/apikey) 🔑"
        )

    # Instruction
    st.write(
        "Upload an image and provide a reasoning-based task for the AI Agent. "
        "The AI Agent will analyze the image and respond based on your input."
    )

    if not gemini_api_key:
        st.warning("Please enter your Gemini API key in the sidebar to continue.")
        return

    # Set up the reasoning agent
    agent = Agent(
        model=Gemini(id="gemini-2.5-pro", api_key=gemini_api_key), 
        markdown=True
    )

    #User prompt
    task_input = st.text_area(
                "Enter your task/question for the AI Agent:"
            )
    
    # File uploader for image
    uploaded_files = st.file_uploader("Upload Image", accept_multiple_files=True)
    # uploaded_file = st.file_uploader("Upload Image", accept_multiple_files=True, type=["jpg", "jpeg", "png"])
    # st.warning("Image uploaded successfully.", icon="✅")

    a_button = st.button("Analyze")

    if uploaded_files is not None:
        try:
            # Save uploaded file to temporary file
            images = []
            videos = []
            files = []
            temp_paths = []  # Track all temp files for cleanup
            success=False
            for file in uploaded_files: 
                if file.name.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp')):
                    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.name)[1]) as tmp_file:
                        tmp_file.write(file.getvalue())
                        temp_path = tmp_file.name
                    images.append(Image(filepath=temp_path))
                    temp_paths.append(temp_path)
                    
                elif file.name.lower().endswith(('.mp4', '.avi', '.mov', '.mkv', '.wmv')):
                    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.name)[1]) as tmp_file:
                        tmp_file.write(file.getvalue())
                        temp_path = tmp_file.name
                    videos.append(Video(filepath=temp_path))
                    temp_paths.append(temp_path)
                    
                elif file.name.lower().endswith(('.pdf', '.txt', '.docx', '.doc', '.csv', '.xlsx')):
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                    # with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.name)[1]) as tmp_file:
                        tmp_file.write(file.getvalue())
                        temp_path = tmp_file.name
                    files.append(File(filepath=temp_path))
                    temp_paths.append(temp_path)
                success = True
            if success:
                st.success("Files uploaded successfully.", icon="✅")   

            # Display the uploaded image
            # st.image(uploaded_file, caption="Uploaded Image", use_container_width=True)

            # Input for dynamic task
            # task_input = st.text_area(
            #     "Enter your task/question for the AI Agent:"
            # )

            # Button to process the image and task
            if a_button and task_input:
                with st.spinner("AI is thinking... 🤖"):
                    try:
                        # Build arguments dictionary based on uploaded file types
                        arguments = {}
                        if images:
                            arguments['images'] = images
                        if videos:
                            arguments['videos'] = videos
                        if files:
                            arguments['files'] = files
                        
                        # Call the agent with the dynamic task and appropriate media
                        response: RunOutput = agent.run(task_input, **arguments)
                        
                        # Display the response from the model
                        st.markdown("### AI Response:")
                        st.markdown(response.content)
                    except Exception as e:
                        st.error(f"An error occurred during analysis: {str(e)}")
                    finally:
                        # Clean up all temp files
                        for temp_path in temp_paths:
                            if os.path.exists(temp_path):
                                os.unlink(temp_path)

        except Exception as e:
            st.error(f"An error occurred while processing the image: {str(e)}")
    else:
        if a_button and task_input:
            with st.spinner("AI is thinking... 🤖"):
                try:
                    # Call the agent with the dynamic task and image path
                    response: RunOutput = agent.run(task_input)
                    # response: RunOutput = agent.run(task_input, images=[Image(filepath=temp_path)])
                    
                    # Display the response from the model
                    st.markdown("### AI Response:")
                    st.markdown(response.content)
                except Exception as e:
                    st.error(f"An error occurred during analysis: {str(e)}")
                



if __name__ == "__main__":
    main()
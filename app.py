from dotenv import load_dotenv
load_dotenv()

import streamlit as st
import os
from PyPDF2 import PdfReader
from langchain.schema import Document
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains.question_answering import load_qa_chain
from langchain.prompts import PromptTemplate

# Load API key
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Function: Extract text from PDF and return as LangChain Document list
def input_pdf_setup(uploaded_file):
    if uploaded_file is not None:
        reader = PdfReader(uploaded_file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""   # extract text safely

        # Wrap inside Document (important for LangChain)
        docs = [Document(page_content=text, metadata={"source": uploaded_file.name})]
        return docs
    else:
        raise FileNotFoundError("No file uploaded")

# Function: Get Gemini response using LangChain
def get_gemini_response(input_prompt, docs, jd_text):
    model = ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=GOOGLE_API_KEY)

    # Define QA Chain
    prompt_template = """You are a helpful assistant. 
    Job Description: {job_description}
    Resume Content: {context}
    Task: {input_prompt}
    """
    PROMPT = PromptTemplate(
        template=prompt_template,
        input_variables=["job_description", "context", "input_prompt"]
    )
    chain = load_qa_chain(model, chain_type="stuff", prompt=PROMPT)

    response = chain(
        {"input_documents": docs, "job_description": jd_text, "input_prompt": input_prompt},
        return_only_outputs=True
    )
    return response["output_text"]

# ------------------ Streamlit UI ------------------
st.set_page_config(page_title="ATS Resume Expert")
st.header("ATS Tracking System")

input_text = st.text_area("Job Description: ", key="input")
uploaded_file = st.file_uploader("Upload your resume (PDF)...", type=["pdf"])

if uploaded_file is not None:
    st.write("PDF Uploaded Successfully")

submit1 = st.button("Tell Me About the Resume")
submit3 = st.button("Percentage Match")

# Prompts
input_prompt1 = """
You are an experienced Technical Human Resource Manager, your task is to review the provided resume against the job description. 
Please share your professional evaluation on whether the candidate's profile aligns with the role. 
Highlight the strengths and weaknesses of the applicant in relation to the specified job requirements.
"""

input_prompt3 = """
You are a skilled ATS (Applicant Tracking System) scanner with a deep understanding of data science and ATS functionality. 
Your task is to evaluate the resume against the provided job description. 
Give me the percentage of match if the resume matches the job description. 
First output should come as percentage, then keywords missing, and finally final thoughts.
"""

if submit1:
    if uploaded_file is not None:
        docs = input_pdf_setup(uploaded_file)
        response = get_gemini_response(input_prompt1, docs, input_text)
        st.subheader("The Response is")
        st.write(response)
    else:
        st.write("Please upload the resume")

elif submit3:
    if uploaded_file is not None:
        docs = input_pdf_setup(uploaded_file)
        response = get_gemini_response(input_prompt3, docs, input_text)
        st.subheader("The Response is")
        st.write(response)
    else:
        st.write("Please upload the resume")

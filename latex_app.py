import streamlit as st
import subprocess
import os
import base64
from langchain.chat_models import ChatOpenAI
from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    AIMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain.schema import AIMessage, HumanMessage, SystemMessage
import re
import pandas as pd
import reveal_slides as rs
import markdown
import time

def extract_markdown_between_delimiters(text):
    delimiter = '---'
    lines = text.strip().split('\n')

    start_index = None
    end_index = None

    for i, line in enumerate(lines):
        if line.strip() == delimiter:
            if start_index is None:
                start_index = i
            else:
                end_index = i
                break

    if start_index is not None and end_index is not None:
        markdown_lines = lines[start_index + 1 : end_index]
        extracted_markdown = '\n'.join(markdown_lines)
        return extracted_markdown
    else:
        return None




df_competition = pd.read_csv('startups.csv', sep = ';')
openai = ChatOpenAI(
    	model_name="gpt-3.5-turbo-16k",
    	temperature=0.7,
    	openai_api_key='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', #openai_key
	)	


def displayPDF(file):
    # Opening file from file path
    with open(file, "rb") as f:
        base64_pdf = base64.b64encode(f.read()).decode('utf-8')

    # Embedding PDF in HTML
    pdf_display = F'<embed src="data:application/pdf;base64,{base64_pdf}" width="1000" height="1000" type="application/pdf">'

    # Displaying File
    st.markdown(pdf_display, unsafe_allow_html=True)
    
    
def filter_beamer(multi_line_string): 
    latex_match = re.search(r'\\documentclass.*?\\end{document}', multi_line_string, re.DOTALL)
    if latex_match:
        latex_document = latex_match.group(0)
        print(latex_document)
    else:
        print("No LaTeX document found.")
        latex_document = ''
    return latex_document


def generate_pitch_deck(user_prompt,competition,team,market_analysis,traction):

    prompt ="""Please create a pitch-deck style presentation on the following topic using reveal.js Markdown code. Topic: """ + str(user_prompt) + """. Please provide only Markdown code for the reveal.js slides:
    1. Project title and team""" +  str(team) +  """
    2. Problem and target audience
    3. Description and Value proposition of the startup
    4. Key competition summary and insights according to the given table:""" + competition + """
    5. Market Analysis estimates""" + market_analysis +"""
    6. Traction and Roadmap""" + traction + """
     Provide only Markdown code.""" 
    messages = [
    SystemMessage(
        content="you are PitchDeckGPT: you create a pitch-deck style presentations from plain text into reveal.js Markdown format. You answer only with correct Markdown code according to reveal.js format for slides and bullet points."
    ),
    HumanMessage(
        content=prompt
    ),
]


    output = openai(messages).content
    print(output)
    return output

def classify_area(problem):
    prompt = """Based on the following startup value introduction, answer with the most fitting class of tech for the startup from the list. Please give only the class in answer.:
 Business Software',
 'IndustrialTech',
 'E-commerce',
 'Advertising & Marketing',
 'Hardware',
 'RetailTech',
 'ConstructionTech',
 'Web3',
 'EdTech',
 'Business Intelligence',
 'Cybersecurity',
 'HrTech',
 'Telecom & Communication',
 'Media & Entertainment',
 'FinTech',
 'MedTech',
 'Transport & Logistics',
 'Gaming',
 'FoodTech',
 'AI',
 'WorkTech',
 'Consumer Goods & Services',
 'Aero & SpaceTech',
 'Legal & RegTech',
 'Travel',
 'PropTech',
 'Energy',
 'GreenTech'
Startup introduction: """ + str(problem)
    
    messages = [
    HumanMessage(
        content=prompt
    ),
    ]


    output = openai(messages).content
    print(output)
    return output


def get_competitors(df,class_name):
    return df[df['Рынок']==class_name].dropna(axis='columns').to_string()

st.title("Pitchdeck Generator")
output = ""
with st.sidebar:
    openai_key = st.sidebar.text_area("openAI API key")
    # Text input for LaTeX content
    latex_input = st.sidebar.text_area("Enter your presentation tKeyopic here:")
    team_input = st.sidebar.text_area("Enter your team")
    proposition_input = st.sidebar.text_area("Enter your startup proposition")
    traction_input = st.sidebar.text_area("Enter your roadmap and traction")
    market_input= st.sidebar.text_area("Enter your Market study")

    if len(latex_input)==0:
        output = """"""

button = st.button("Compile and Display PDF") 
if button and len(latex_input)!=0:
    with st.spinner("Running a long computation.."):
        area = classify_area(proposition_input)
        competition = get_competitors(df_competition,str(area))
        output = generate_pitch_deck(latex_input,competition,team_input,market_input,traction_input)
        print(output)
        html_output = markdown.markdown(output)

# Save the HTML output to a file
        with open('output.html', 'w') as f:
            f.write(html_output)
            print("HTML content saved to 'output.html'")


        
response_dict = rs.slides(extract_markdown_between_delimiters(output))


        

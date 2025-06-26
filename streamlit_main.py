import requests
from io import BytesIO
import streamlit as st
from streamlit_ace import st_ace
from concepts_parser import main, post_process_parser
import os

# option = st.selectbox("Select Programming Language",("python","java"))
url = 'http://adapt2.sis.pitt.edu/w/images/1/19/PAWS_logo.png'
img_b = requests.get(url)
favicon = BytesIO(img_b.content).read()

st.set_page_config(page_title="PCCP",
                   page_icon=favicon)

st.title("University of Pittsburgh: PAWSLab Python Code Concepts Parser (PCCP)")
st.image('http://adapt2.sis.pitt.edu/w/images/1/19/PAWS_logo.png')

code_string = """
### enter code here

""" \
# if option == 'python' else \
# """
# // enter code here
# """

with st.form("code_form"):
    code = st_ace(value=code_string,
                language="python",
                min_lines= 50,
                max_lines=500,
                auto_update=True,
                theme="dracula")

    submitted = st.form_submit_button("Submit Code")

    if submitted:
        if not(os.path.exists('./py-files')): os.mkdir('py-files')
        with open(f'./py-files/tmp1.py','w+') as f:
            f.write(code)

        codelines, response = main(filename='py-files/tmp1.py')
        st.dataframe(post_process_parser(response))

        os.remove('./py-files/tmp1.py')
        os.rmdir('./py-files')

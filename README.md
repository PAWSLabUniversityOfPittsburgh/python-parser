# Python parser

This Acos server tool parses Python 3 code and
returns the found concepts by traversing the AST
of the code.


## Requires 
Python==3.9.22

## To run frontend
python3.9 -m streamlit run streamlit_main.py

## To run API
python3.9 -m uvicorn main_api:app --reload-include="main_api.py" --reload-exclude="*/py-files/*"
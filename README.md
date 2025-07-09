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

## Deployment on PAWSComp

```
sudo docker stop python-parser-api-container

sudo docker rm python-parser-api-container

sudo docker run --privileged=true -d --name python-parser-api-container -p 13456:13456 python-parser-api

curl -X POST http://127.0.0.1:13456/extract_concepts -H "Content-Type: application/json" -d '{"code_str":"import txt"}'

curl -X POST http://127.0.0.1:13456/extract_concepts -H "Content-Type: application/json" -d '{"code_str":"import txt\ntest=1"}'

curl -X POST http://127.0.0.1:13456/extract_concepts -H "Content-Type: application/json" -d '{"code_str":"s='hola'\ns[0:2]"}'
```

Expected output:
```
Import_alias

Assign_Import_Int_alias

Int_Assign_Slice_Str
```

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

curl -X POST http://127.0.0.1:13456/extract_concepts -H "Content-Type: application/json" -d '{"code_str":"s='hola'"}'

curl -X POST http://127.0.0.1:13456/extract_concepts -H "Content-Type: application/json" -d '{"code_str":"s='hola'\ns[0:2]"}'
```

Expected output:
```
[{"content_id":143,"section_id":"tmp1","concept":"Import_alias","resource_id":"pfe","is_active":1,"date_added":"2025-07-09 19:15:09"}]

[{"content_id":143,"section_id":"tmp1","concept":"Assign","resource_id":"pfe","is_active":1,"date_added":"2025-07-09 19:19:48"}]

[{"content_id":143,"section_id":"tmp1","concept":"Assign_Slice_Int","resource_id":"pfe","is_active":1,"date_added":"2025-07-09 19:21:05"}]
```

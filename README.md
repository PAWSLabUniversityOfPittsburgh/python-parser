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
sudo su
source setup_docker.sh
exit
```

Then to test

```
source test_docker.sh
```

Expected output:
```
[{"content_id":143,"section_id":"tmp1","concept":"Import_alias","resource_id":"pfe","is_active":1,"date_added":"2025-07-09 19:15:09"}]

[{"content_id":143,"section_id":"tmp1","concept":"Assign","resource_id":"pfe","is_active":1,"date_added":"2025-07-09 19:19:48"}]

[{"content_id":143,"section_id":"tmp1","concept":"Assign_Slice_Int","resource_id":"pfe","is_active":1,"date_added":"2025-07-09 19:21:05"}]
```

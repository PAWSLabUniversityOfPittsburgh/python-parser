from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from concepts_parser import main, post_process_parser
import os

app = FastAPI()

class CodeString(BaseModel):
    """
    Custom type for code strings.
    This can be extended with validation if needed.
    """
    content_id: int = 123
    code_str: str = ""
    section_id: str = ""
    resource_id: str = ""
    is_active: int = 1  # Default value for is_active
    date_added: str = None  # Default value for date_added

@app.get("/test_api")
async def test_api():
    return {"message": "API is working!"}


@app.post("/extract_concepts")
async def extract_concepts(code_json: CodeString):
    print(code_json)
    
    if code_json is None:
        raise HTTPException(status_code=400, detail="Code string cannot be empty")
    try:
        code_str = code_json.code_str.strip()
        # Create a temporary directory for the code file
        if not os.path.exists('./py-files'):
            os.mkdir('py-files')

        # Write the code to a temporary file
        with open('./py-files/tmp1.py', 'w+') as f:
            f.write(code_str)

        # Extract concepts from the code
        codelines, response = main(filename='py-files/tmp1.py')
        
        # Clean up the temporary files
        os.remove('./py-files/tmp1.py')
        os.rmdir('./py-files')

        response_df =  post_process_parser(response)
        return response_df.to_dict(orient='records')
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

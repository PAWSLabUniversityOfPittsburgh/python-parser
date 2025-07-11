FROM python:3.9.22

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN pip install --progress-bar off --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./ /code/

CMD ["fastapi", "run", "main_api.py", "--port", "13456"]

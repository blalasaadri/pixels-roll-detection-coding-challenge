FROM python:alpine3.18

WORKDIR /usr/src/app

COPY src ./
RUN pip install --no-cache-dir -r requirements.txt

ENTRYPOINT [ "python", "./start.py" ]

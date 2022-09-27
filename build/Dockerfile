FROM python:3.9

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
ENV PYTHONUNBUFFERED 1
ENV PYTHONIOENCODING UTF-8

COPY ./src .

CMD [ "python", "./main.py" ]

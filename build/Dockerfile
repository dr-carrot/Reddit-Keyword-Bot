FROM python:3.9

WORKDIR /usr/src/app

COPY build/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
ENV PYTHONUNBUFFERED 1
ENV PYTHONIOENCODING UTF-8
ENV PYTHONPATH /usr/src/app

COPY ./src .

CMD [ "python", "main.py" ]

FROM python:3.7-slim-buster

WORKDIR /
ENV FLASK_APP route.py



COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
COPY . .

CMD ["flask", "run", "--host=0.0.0.0"]

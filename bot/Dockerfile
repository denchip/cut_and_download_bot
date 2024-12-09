FROM python:3.9

RUN apt-get update -qq && apt-get install ffmpeg -y

COPY requirements.txt requirements.txt
RUN pip install --upgrade pip && pip install -r requirements.txt && chmod 755 .

WORKDIR bot
COPY . .
CMD ["python", "-u", "main.py"]

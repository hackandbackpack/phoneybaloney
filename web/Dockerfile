FROM python:3-alpine
WORKDIR /app
COPY web.py /app/web.py
COPY templates/index.html /app/templates/index.html
RUN apk update && apk add --no-cache ffmpeg flac wget 
RUN wget http://161.35.14.175/scenario/scenarios.json
RUN wget http://161.35.14.175/scenario/api_keys.json
RUN pip install --no-cache Flask gunicorn SpeechRecognition ffmpeg-python openai==0.28.0
EXPOSE 8080
CMD ["/bin/sh", "-c", "gunicorn --bind 0.0.0.0:8080 -w 1 web:app"]


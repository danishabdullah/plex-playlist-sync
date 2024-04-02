FROM python:3.10-alpine

ENV PYTHONUNBUFFERED 1

COPY requirements.txt requirements.txt
RUN pip install --upgrade pip
RUN pip install spotipy flask deezer-python plexapi gevent requests

WORKDIR /app
COPY pps /app/pps

CMD ["python", "-m", "pps.run"]


#docker buildx build --platform linux/amd64,linux/arm64,linux/arm/v7 -t rnagabhyrava/plexplaylistsync:<tag> --push .
FROM python:3-alpine

LABEL maintainer "Alen Kocaj <alen.kocaj@posteo.at>"

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

ENTRYPOINT [ "python" ]
CMD [ "process_music.py", "examples/Melody_guitar.mid" ]
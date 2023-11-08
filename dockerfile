FROM python

RUN apt-get update && apt-get install -y ffmpeg

RUN pip install yt-dlp pyTelegramBotAPI

WORKDIR /tv_downloader

COPY tv_downloader.py /tv_downloader

CMD python tv_downloader.py

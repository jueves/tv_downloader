FROM python

RUN apt-get update && apt-get install -y ffmpeg

RUN pip install yt-dlp pyTelegramBotAPI

WORKDIR /tv_downloader

RUN mkdir  /tv_downloader/videos

COPY tv_downloader.py /tv_downloader

RUN groupadd -g 1020 media && useradd -u 1000 -g media tv_downloader

RUN chown tv_downloader:media -R /tv_downloader

USER tv_downloader

ENV UMASK 002

CMD python tv_downloader.py

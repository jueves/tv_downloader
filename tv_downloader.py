import os
import json
import subprocess
from datetime import datetime
import telebot

TELEGRAM_KEY = os.environ.get("TELEGRAM_KEY")
ALLOWED_TELEGRAM_USER = os.environ.get("ALLOWED_TELEGRAM_USER")
HISTORY_FILENAME = "videos/history.json"
VIDEOS_PATH = "videos"
LINKS_FILENAME = "links.txt"
DEFAULT_MAX_HEIGHT = "720"
DEFAULT_SUBPATH = "Varios"

categories = {
    "/ejercicio":{"max_height":"720",
                 "subpath":"Ejercicio"
                 },
    "/estudio":{"max_height":"1080",
                 "subpath":"Estudio"
                 }
    }

def download_video(message):
    '''
    Gets a message with urls and an optional video max resolution height.
    Downloads videos with yt-dlp
    Saves url, date and title to history.
    Returns outcome as a string.
    '''
    user = str(message.from_user.id)
    if user == ALLOWED_TELEGRAM_USER:
        text_list = message.text.split()
        if text_list[0] in categories.keys():
            max_height = categories[text_list[0]]["max_height"]
            subpath = categories[text_list[0]]["subpath"]
            text_list = text_list[1:]
        else:
            max_height = DEFAULT_MAX_HEIGHT
            subpath = DEFAULT_SUBPATH
        if text_list[-1][:4] != "http":
            max_height = text_list.pop()

        reply = yt_dlp_manager(links_list=text_list, max_height=max_height, subpath=subpath)
        update_history(links_list=text_list)
    else:
        reply = ("This is a single user bot, you are not allowed to use it. To deploy"
                " your own check https://github.com/jueves/tv_downloader")
    return reply

def yt_dlp_manager(links_list, max_height=DEFAULT_MAX_HEIGHT, subpath="Varios"):
    '''
    Downloads links in links_list using yt-dlp
    '''
    download_path = VIDEOS_PATH + "/" + subpath

    with open("links.txt", "w", encoding="utf8") as f:
        for url in links_list:
            f.write(url+"\n")

    try:
        yt_command = (f"yt-dlp --add-metadata -f 'bv*[height<={max_height}]+ba\'"
                      " --merge-output-format mkv --embed-metadata "
                      f" -o {download_path}/%\\(title\\)s.%\\(ext\\)s -a {LINKS_FILENAME}")
        subprocess.run(yt_command, shell=True, check=True, capture_output=True, text=True)
        reply = "Video descargado correctamente."
    except subprocess.CalledProcessError as e:
        reply = (f"tv_dowloader error: command '{e.cmd}' return with error"
                 f"(code {e.returncode}): {e.output}")
    return reply

def update_history(links_list):
    '''
    Updates history file with URLs in links_list and each of it's titles.
    '''
    try:
        with open(HISTORY_FILENAME, "r", encoding="utf-8") as f:
            history = json.load(f)
    except FileNotFoundError:
        history = {}

    for url in links_list:
        result = subprocess.run(['yt-dlp', '--get-filename', url],
                                capture_output=True, text=True, check=True)
        video_name = result.stdout.strip()
        history[datetime.now().strftime("%Y/%m/%d %H:%M:%S_%f")] = {"url":url, "name":video_name}

    with open(HISTORY_FILENAME, "w", encoding="utf8") as f:
        json.dump(history, f, indent=4)

bot = telebot.TeleBot(TELEGRAM_KEY)

@bot.message_handler(func=lambda msg: True)
def echo_all(message):
    '''
    Takes all incoming messages and returns answers.
    '''
    def answer(text):
        bot.send_message(message.chat.id, text)

    if message.text == "/start":
        answer("Bienvenido\n"
               "Ejemplos:\n"
               "/categoría url1 url2 url3 resolución_máxima\n"
               "url1 url2\n"
               "url")
    else:
        answer("Descargando video...")
        answer(download_video(message))

bot.infinity_polling()

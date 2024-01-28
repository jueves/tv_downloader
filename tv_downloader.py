import os
import json
import telebot
import subprocess
from datetime import datetime

TELEGRAM_KEY = os.environ.get("TELEGRAM_KEY")
TELEGRAM_USER_ID = os.environ.get("TELEGRAM_USER_ID")
HISTORY_FILE = "videos/history.json"

def download_video(message):
    allowed_user = str(message.from_user.id)
    if allowed_user == TELEGRAM_USER_ID:
        text_list = message.text.split()
        path = "videos"
        if text_list[-1][:4] != "http":
            max_height = text_list.pop()               
        else:
            max_height = "720"

        with open("links.txt", "w") as f:
            for url in text_list:
                f.write(url+"\n")
        try:
            yt_command = f"yt-dlp --add-metadata -f 'bv*[height<={max_height}]+ba\' -o {path}/%\(title\)s.%\(ext\)s -a links.txt" 
            subprocess.run(yt_command, shell=True, check=True, capture_output=True, text=True)
            update_history(url_list=text_list)
            reply = "Video downloaded succesfully."
        except subprocess.CalledProcessError as e:
            reply = f"An error occurred: {e}"
    else:
        reply = "This is not going to work."
    return(reply)

def update_history(url_list):
    '''
    Updates history file with URLs in url_list and each of it's titles.
    '''
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            history = json.load(f)
    except FileNotFoundError:
        history = {}

    for url in url_list:
        result = subprocess.run(['yt-dlp', '--get-filename', url],
                                capture_output=True, text=True, check=True)
        video_name = result.stdout
        history[datetime.now().strftime("%Y/%m/%d %H:%M:%S_%f")] = {"url":url, "name":video_name}

    with open(HISTORY_FILE, "w", encoding="utf8") as f:
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
        answer("Hi")
    else:
        answer("Downloading video...")
        answer(download_video(message))

bot.infinity_polling()

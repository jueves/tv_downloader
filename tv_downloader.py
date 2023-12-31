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
        url = message.text
        path = "videos"
        try:
            result = subprocess.run(['yt-dlp', '--get-filename', url],
                                    capture_output=True, text=True, check=True)
            video_name = result.stdout
            print("----------------VIDEO NAME:\n" + video_name)
            subprocess.run(['yt-dlp', '--add-metadata', '-o', f'{path}/%(title)s.%(ext)s',
                            url], check=True)
            update_history(url, video_name)
            reply = "Video downloaded succesfully."
        except subprocess.CalledProcessError as e:
            reply = f"An error occurred: {e}"
    else:
        reply = "This is not going to work."
    return(reply)

def update_history(url, video_name):
    # Updates history file with the new succesfull download URL.
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            history = json.load(f)
    except FileNotFoundError:
        history = {}

    history[datetime.now().strftime("%Y/%m/%d %H:%M:%s")] = {"url":url, "name":video_name}
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

from db import connection, cursor, set_user_name, get_user_name, set_user_state, get_user_state, token, group_id, table
from dotenv import load_dotenv
from flask import Flask, request, render_template, redirect, send_from_directory
from apscheduler.schedulers.background import BackgroundScheduler
import requests
import os
import time
import db
import sqlite3 as sq


Telegram_API = f"https://api.telegram.org/bot{token}"

user_state = "WAITING_NAME"
state_idle = "idle"


def ping_websites():
    print(f"\n[{time.strftime('%Y-%m-%d %H:%M:%S')}] Pinging websites...")
    websites = [
        "https://www.vectorsauto.com",
        "https://vectorstutor.onrender.com"
    ]
    for url in websites:
        try:
            response = requests.get(url, timeout=10)
            print(f"Pinged {url} - Status: {response.status_code}")
        except Exception as e:
            print(f"Failed to ping {url}: {e}")


app = Flask(__name__, static_folder="static")

app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

@app.route("/webhook", methods = ["POST"])
def webhook():
    global user_state
    
    update = request.get_json()
    
    if "message" in update:
        table()
        print(update)
        message = update["message"]
        chat_id = message["chat"]["id"]
        text = message.get("text", "")
        
        if text == "/start":
            
            set_user_state(chat_id, user_state)
            send_message(chat_id, "👋 Hello! Welcome to Vectors Telegram bot. What is your name?")
   
            return "OK"
        
        user_state = get_user_state(chat_id)
        print(f"\n{user_state}\n")

        if user_state == "WAITING_NAME":
            name = text.strip()
            print(name)
            set_user_name(chat_id, name)
            set_user_state(chat_id, state_idle)
            print("\nI am waiting here\n")
            send_button(chat_id, f"You are highly welcome {get_user_name(chat_id)}! Don\'t panic. You are safe in the Milky Way galaxy.\n Feel free to explore the bot. If you like, you can join the Python Heroes group at {invite_link(group_id)}")
        #    send_message(chat_id, "Weldone")
            return "OK"
        

    if "callback_query" in update:
        print("\nA button clicked\n")
        
        
        callback = update["callback_query"]
        chat_id = callback["message"]["chat"]["id"]
        data = callback["data"]
            
        if data == "ABOUT":
            func_about(chat_id)
            
        elif data == "HELP":
            send_button(chat_id, f"I am sorry {get_user_name(chat_id)}! I can\'t do any assistance for you. Only Almighty God can help.")
        elif data == "GAMES":
            send_button(chat_id, f"We are so sorry {get_user_name(chat_id)}! Games are coming soon. Stay informed.")
            
        elif data == "EXPLORE":
            send_button(chat_id, "Sorry! Nothing to explore yet. Lateef (Vectors) is just playing.")  
            
            
    return "OK"
  



@app.route("/")
def index():
    return render_template("index.html")

@app.route("/signup")
def signup():
    return render_template("signup.html")


# -------------------------------------------------------------------------------- Above contains decorator functions only.


def web_app(chat_id):
    url = f"{Telegram_API}/sendMessaage"
    keyboard = {"inline_keyboard" : [
        [{"text": "Sign in" }]
        ]}

            
def send_message(chat_id, text):
    payload = {"chat_id": chat_id, "text": text}
    
    response = requests.post(f"{Telegram_API}/sendMessage", json = payload)
    print(response.text)
    
def func_about(chat_id):
    message = "🤖 This bot was built by Lateef Olayinka Basiru (Vectors) in Obafemi Awolowo University Ile-Ife Nigeria using Flask, the python's framework, the required telegram API and some other tools. This bot is currently being upgraded. This bot has been modified for ongoing trianing known as Python Heroes where tech lovers are learning Python Programming language."
    payload = {"chat_id": chat_id, "text": message}
    requests.post(f"{Telegram_API}/sendMessage", payload)

  
def func_help(chat_id):
    message = "🤖 Only Almighty God can help."
    payload = {"chat_id": chat_id, "text": message}
    requests.post(f"{Telegram_API}/sendMessage", payload)
  
  
  


  

def send_button(chat_id, text, image = None):
    
    print("Keyboard reached")
    keyboard = {"inline_keyboard": [
        [{"text": "Explore the app", "callback_data": "EXPLORE"}],
        [{"text": "Online games", "callback_data": "GAMES"}],
        [{"text": "ℹ️ About", "callback_data": "ABOUT"}],
        [{"text": "🆘 Help", "callback_data": "HELP"}],
        [{"text": "Sign in 🌍", "web_app": {"url" : "https://google.com"}}]   #  https://addison-raring-chelsea.ngrok-free.dev"+"/webapp"}}]  
    ]}

 
    print("On payload")
    payload = {"chat_id": chat_id, "text": text, "reply_markup": keyboard}
    print("On requests")
    requests.post(f"{Telegram_API}/sendMessage", json = payload)
    
def invite_link(chat_id):
    api = f"{Telegram_API}/createChatInviteLink"
    
    payload = {
        "chat_id": chat_id,
        "member_limit": 1,
        "expire_date": int(time.time()) + 7200
       
        }
    
    response = requests.post(api, payload)
    return response.json()["result"]["invite_link"]
    
#  -------------------------------------------------------------------------------------------------------------------------------

#  -------------------------------------------------------------------------------------------------------------------------------

if __name__ == "__main__":
    # Initialize scheduler
    scheduler = BackgroundScheduler()
    # Add ping job to run every 3 minutes
    scheduler.add_job(func=ping_websites, trigger="interval", minutes=3)
    # Start the scheduler
    scheduler.start()
    print("Scheduler started. Pinging websites every 3 minutes.")

    # Run the Flask app
    app.run(debug=True, port=5000, use_reloader=False)


    
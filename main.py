import json
import socketio
import telebot
from telebot import types
from telebot import apihelper

config = json.loads(open("config.json").read())

token = config["tg_token"]

bot = telebot.TeleBot(token)
telebot.apihelper.proxy = {"https": "socks5://localhost:9050"}

sio = socketio.Client()

ready = False
ready_chat = False
user_id = None
player_name = None
scores_data = None
output_chat_message = None

sio.connect("ws://45.77.109.150:2000")

@sio.on("handshake")
def on_handshake(data):
	global user_id
	user_id = data["socketId"]
	print(user_id)
	sio.emit("createPlayer", {"spawn": "guinea"})

@sio.on("scores")
def message(data):
	global ready
	if ready == True:
		return
	global scores_data
	scores_data = data["players"]
	for player in scores_data:
		if player["id"] == user_id:
			global player_name
			player_name = player["name"]
			print("ID: " + player["id"] + "\nNAME: " + player["name"] + "\nPARENTID: " + player["parentId"])
			ready = True

@bot.message_handler(commands=["stop"])
def handle_stop(message):
	bot.send_message(message.chat.id, "See you soon!")
	sio.disconnect()

@bot.message_handler(commands=["start"]) 
def handle_start(message):
	bot.send_message(message.chat.id, "Welcome to chat KrewIO, " + player_name + "!")
	global ready_chat
	ready_chat = True

	@sio.on("chat message")
	def get_chat_message(data):
		if ready_chat == True:	
			global player_name
			if data["playerName"] != player_name:
				bot.send_message(message.chat.id, "*" + data["playerName"] + ": " +"*" + data["message"], parse_mode="Markdown")

@bot.message_handler(content_types=["text"])
def send_message(message):
	if message.text[0] != "/":
		sio.emit("chat message", {"message": message.text, "recipient": "global"})

if __name__ == "__main__":
	bot.infinity_polling()
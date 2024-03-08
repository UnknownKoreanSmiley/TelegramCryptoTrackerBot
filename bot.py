import asyncio
import json
import os
import traceback
from dotenv import load_dotenv
import requests
import telebot
import websockets

# Load environment variables from .env file
load_dotenv()

# Telegram bot token and chat ID
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# Initialize 
bot = telebot.TeleBot(BOT_TOKEN)

# Global variables
selected_coin = ''
graph_image = False
current_position = 0
previous_close_price = 0
previous_message_id = None
is_connected = False
websocket = None

# Fetch available coins from API
def fetch_coins():
    response = requests.get('https://whitebit.com/api/v1/public/symbols')
    if response.status_code == 200:
        return json.loads(response.text)['result']
    else:
        print(f"Failed to fetch coins. Status code: {response.status_code}")
        return []

# Send welcome message
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, f"Hello {message.from_user.first_name}!")

# Handle callback queries
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    global current_position, selected_coin, graph_image
    if call.data == "Next":
        current_position += 10
        update_coin_next_prev(call.message)
    elif call.data == "Previous":
        current_position -= 10
        update_coin_next_prev(call.message)
    elif call.data == 'CloseSocket':
        if call.message:
            bot.delete_message(call.message.chat.id, call.message.message_id)
        if is_connected and websocket:
            asyncio.run(close_websocket())
    elif call.data == 'GraphImage':
        if not graph_image:
            send_graph_image(call.message, False)
    elif call.data == 'UpdateGraph':
        send_graph_image(call.message, True)
    else:
        selected_coin = call.data 
        asyncio.run(connect_and_send_message())

# Send graph image
def send_graph_image(message, edit):
    global graph_image
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(telebot.types.InlineKeyboardButton(text="Update", callback_data="UpdateGraph"))
    try:
        time_response = requests.get("https://whitebit.com/api/v4/public/time")
        if time_response.status_code == 200:
            timestamp = time_response.json()['time']
            image_url = f"https://bff.whitebit.com/v1/canvas/ogImage/trade/{selected_coin}.png?t={timestamp}"
            image_response = requests.get(image_url)
            if image_response.status_code == 200:
                image_data = image_response.content
                graph_image = True
                if not edit:
                    bot.send_photo(chat_id=message.chat.id, photo=image_data, reply_markup=markup)
                else:
                    bot.edit_message_text(chat_id=str(CHAT_ID), message_id=message.message_id, text="Updated message text.",reply_markup=markup)
                    bot.edit_message_media(chat_id=message.chat.id, message_id=message.message_id, media=telebot.types.InputMediaPhoto(media=image_data),reply_markup=markup)
            else:
                print(f"Failed to download image. Status code: {image_response.status_code}")
        else:
            print(f"Failed to fetch timestamp. Status code: {time_response.status_code}")
    except Exception as e:
        print(f"An error occurred: {e}")

# Send available coins
@bot.message_handler(commands=['coins'])
def send_coins(message):
    coins = fetch_coins()
    markup = telebot.types.InlineKeyboardMarkup()
    for single_coin in coins[current_position:current_position+10]:
        markup.add(telebot.types.InlineKeyboardButton(text=single_coin, callback_data=single_coin))
    if current_position + 10 < len(coins):
        markup.add(telebot.types.InlineKeyboardButton(text="Next", callback_data="Next"))
    if current_position > 0:
        markup.add(telebot.types.InlineKeyboardButton(text="Previous", callback_data="Previous"))
    bot.send_message(message.chat.id, "Choose a coin:", reply_markup=markup)

# Update next and previous buttons for coins
def update_coin_next_prev(message):
    coins = fetch_coins()
    markup = telebot.types.InlineKeyboardMarkup()
    for single_coin in coins[current_position:current_position+10]:
        markup.add(telebot.types.InlineKeyboardButton(text=single_coin, callback_data=single_coin))
    if current_position + 10 < len(coins):
        markup.add(telebot.types.InlineKeyboardButton(text="Next", callback_data="Next"))
    if current_position > 0:
        markup.add(telebot.types.InlineKeyboardButton(text="Previous", callback_data="Previous"))
    bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text="Choose a coin:", reply_markup=markup)

# Connect and send market data(websocket)
async def connect_and_send_message():
    global is_connected, websocket, graph_image
    graph_image = False
    uri = "wss://api.whitebit.com/ws"
    while True:
        try:
            if is_connected:
                await websocket.close()
            async with websockets.connect(uri) as websocket:
                is_connected = True
                message = {
                    "id": 6,
                    "method": "market_subscribe",
                    "params": [selected_coin]
                }
                await websocket.send(json.dumps(message))
                while True:
                    data = await websocket.recv()
                    handle_data(data)
                    await asyncio.sleep(2) 
        except websockets.exceptions.ConnectionClosedError:
            print("Connection closed, attempting to reconnect...")
            await asyncio.sleep(5) 
        except Exception as e:
            print(f"An error occurred: {e}")
            traceback.print_exc()
            break  

# Close websocket connection
async def close_websocket():
    global is_connected, websocket
    if is_connected == False:
        return
    message = {
        "id": 6,
        "method": "market_unsubscribe",
        "params": [selected_coin]
    }
    await websocket.send(json.dumps(message))
    is_connected = False

# handle incoming market data
async def handle_data(data):
    global previous_close_price, previous_message_id, graph_image
    try:
        parsed_data = json.loads(data)
        if "params" in parsed_data and len(parsed_data["params"]) == 2:
            pair, market_data = parsed_data["params"]
            close_price = float(market_data.get("close"))
            open_price = float(market_data.get("open"))
            high_price = float(market_data.get("high"))
            low_price = float(market_data.get("low"))
            volume = float(market_data.get("volume"))
            last_price = float(market_data.get("last"))
            close_indicator = "🔴" if close_price < previous_close_price else "🟢" if previous_close_price is not None else ""
            message_text = f"{pair}  ({close_indicator})\n" \
                           f"---------------------------------\n" \
                           f"Open : {open_price}\n" \
                           f"Close : {close_price}\n" \
                           f"High : {high_price}\n" \
                           f"Low : {low_price}\n" \
                           f"Volume : {volume}\n" \
                           f"Last : {last_price}\n"
            markup = telebot.types.InlineKeyboardMarkup()
            if not graph_image:
                markup.add(telebot.types.InlineKeyboardButton(text="Image", callback_data="GraphImage"))
            markup.add(telebot.types.InlineKeyboardButton(text="Close", callback_data="CloseSocket"))
            try:
                if previous_message_id:
                    bot.edit_message_text(chat_id=str(CHAT_ID), message_id=previous_message_id, text=message_text, reply_markup=markup)
                else:
                    sent_message = bot.send_message(chat_id=str(CHAT_ID), text=message_text, reply_markup=markup)
                    previous_message_id = sent_message.message_id
            except Exception as e:
                await asyncio.sleep(30) 
            previous_close_price = close_price
    except Exception as e:
        print(f"An error occurred while handling data: {e}")
        await asyncio.sleep(30) 
        traceback.print_exc()

# start bot polling
bot.infinity_polling()

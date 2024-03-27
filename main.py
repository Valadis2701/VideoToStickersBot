import telebot
from telebot import types
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import time
import yaml
import importlib
from time import sleep

# Load configuration from config.yml
with open("config.yml", "r") as f:
    config = yaml.safe_load(f)

BOT_TOKEN = config["bot_token"]
ADMIN_IDS = config["admin_ids"]
LANGUAGE = config["language"].upper()  # Convert language code to uppercase

# Dynamically import language-specific messages
messages = importlib.import_module(f"messages_{LANGUAGE}")

# Create a Telegram bot instance
bot = telebot.TeleBot(BOT_TOKEN)

# Database setup using SQLAlchemy (modified Pair model)
Base = declarative_base()

class Pair(Base):
    __tablename__ = "pairs"
    id = Column(Integer, primary_key=True)
    sticker_id = Column(String, unique=True)
    video_file_id = Column(String)  # Store video file ID instead of path
    creator_id = Column(Integer)  # Store creator's user ID

engine = create_engine("sqlite:///sticker_videos.db")
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

# Function to add a sticker-video pair (modified to check for existing sticker and validate input)
def add_pair(message):
    chat_id = message.chat.id

    # Request sticker from the user first
    bot.send_message(chat_id, messages.add_pair_sticker_request)
    bot.register_next_step_handler(message, add_pair_check_sticker)

def add_pair_check_sticker(message):
    chat_id = message.chat.id
    if not message.sticker:  # Check if it's actually a sticker
        bot.send_message(chat_id, messages.invalid_input_sticker_required)
        return  # Exit the function if not a sticker

    sticker = message.sticker

    # Check if a pair with this sticker already exists
    existing_pair = session.query(Pair).filter_by(sticker_id=sticker.file_unique_id).first()
    if existing_pair:
        bot.send_message(chat_id, messages.sticker_already_paired)
        return  # Exit the function if the sticker is already paired

    # Request video from the user
    bot.send_message(chat_id, messages.add_pair_video_request)
    bot.register_next_step_handler(message, add_pair_get_video, sticker)  # Pass sticker object

def add_pair_get_video(message, sticker):
    chat_id = message.chat.id
    if not message.video:  # Check if it's actually a video
        bot.send_message(chat_id, messages.invalid_input_sticker_required)
        return  # Exit the function if not a video

    # Get video file ID
    video_file_id = message.video.file_id

    # Insert pair into database
    pair = Pair(sticker_id=sticker.file_unique_id, video_file_id=video_file_id, creator_id=message.from_user.id)
    session.add(pair)
    session.commit()

    bot.send_message(chat_id, messages.add_pair_success)

# Function to delete a sticker-video pair (modified to allow admins and validate input)
def delete_pair(message):
    chat_id = message.chat.id
    if not message.sticker:  # Check if it's actually a sticker
        bot.send_message(chat_id, messages.invalid_input_sticker_required)
        return  # Exit the function if not a sticker

    sticker = message.sticker
    user_id = message.from_user.id  # Get user ID of the requester

    # Delete pair from database if the user is the creator or an admin
    pair = session.query(Pair).filter_by(sticker_id=sticker.file_unique_id).first()
    if pair and (pair.creator_id == user_id or user_id in ADMIN_IDS):
        session.delete(pair)
        session.commit()
        bot.send_message(chat_id, messages.delete_pair_success)
    else:
        # Handle non-existent pair
        bot.send_message(chat_id, messages.delete_pair_404)  # Send "pair not found" message

# Function to handle incoming stickers in group chats (with exception handling and input validation)
@bot.message_handler(func=lambda message: message.chat.type != "private", content_types=["sticker"])
def handle_sticker(message):
    if not message.sticker:  # Check if it's actually a sticker
        bot.send_message(message.chat.id, messages.invalid_input_sticker_required)
        return  # Exit the function if not a sticker

    sticker = message.sticker
    username = message.from_user.username  # Get username of the sender

    try:
        # Check if pair exists in database
        pair = session.query(Pair).filter_by(sticker_id=sticker.file_unique_id).first()
        if pair:
            video_file_id = pair.video_file_id  # Get video file ID

            # Check if the video still exists
            bot.get_file(video_file_id)  # This will raise an error if the file doesn't exist

            # Check if the sticker is a reply to a message
            reply_to_message_id = message.reply_to_message.message_id if message.reply_to_message else None
            if reply_to_message_id:
                # Reply to the original message with the video
                caption = f"Ответ {username}:\n"
                bot.send_video(message.chat.id, video_file_id, caption=caption, reply_to_message_id=reply_to_message_id)
            else:
                # Send the video as a regular message
                caption = f"Ответ {username}:\n"
                bot.send_video(message.chat.id, video_file_id, caption=caption)

            # Delete the sticker message
            bot.delete_message(message.chat.id, message.message_id)

    except telebot.apihelper.ApiException as e:
        # Handle video retrieval error
        print(f"Error retrieving video file: {e}")
        bot.send_message(message.chat.id, messages.video_unavailable)

        # Delete the pair from the database if the video is gone
        if pair:
            session.delete(pair)
            session.commit()

# Command handlers (modified to check for private chat)
@bot.message_handler(commands=["start", "addpair", "delpair"])
def handle_commands(message):
    if message.chat.type == "private":
        # Handle commands only in private chats
        if message.text == "/start":
            handle_start(message)
        elif message.text == "/addpair":
            add_pair(message)  # Call the add_pair function directly
        elif message.text == "/delpair":
            handle_del_pair(message)
    else:
        # Ignore commands in group chats
        pass

# Command handlers
@bot.message_handler(commands=["start"])
def handle_start(message):
    chat_id = message.chat.id

    # Send start message parts
    bot.send_message(chat_id, messages.start_message_part1)
    time.sleep(1)
    bot.send_message(chat_id, messages.start_message_part2)
    time.sleep(1)
    bot.send_message(chat_id, messages.start_message_part3)

@bot.message_handler(commands=["delpair"])
def handle_del_pair(message):
    bot.send_message(message.chat.id, messages.delete_pair_request)
    bot.register_next_step_handler(message, delete_pair)

# Start the bot
while True:
    try:
        bot.polling(none_stop=True)
    except Exception as _ex:
        print(_ex)
        sleep(15)
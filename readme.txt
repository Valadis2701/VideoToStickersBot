Telegram Video Stickers Bot
This project is a Telegram bot that allows users to associate stickers with videos. When a user sends a paired sticker in a group chat, the bot will replace it with the corresponding video.
Features:
Pair stickers with videos.
Send videos in response to paired stickers in group chats.
Delete sticker-video pairs.
Admin users can delete any pair.
Video existence check before sending.
Maximum video file size limit (8 MB).
Configuration stored in config.yml.
Docker deployment support.
Deployment Instructions:
Clone the repository:
git clone https://github.com/valadis2701/telegram-video-stickers-bot.git
Install dependencies:
cd telegram-video-stickers-bot
pip install -r requirements.txt
Configure the bot:
Rename config_example.yml to config.yml.
Edit config.yml and replace the placeholder values with your actual bot token and admin IDs.
Build the Docker image:
docker build -t sticker-video-bot .
Run the container:
docker run sticker-video-bot
Start the bot:
Send the /start command to the bot in a private chat to get instructions and start using it.
Usage:
Adding pairs: Send the /addpair command to the bot in a private chat. Send the video first, followed by the sticker you want to pair it with.
Deleting pairs: Send the /delpair command to the bot in a private chat, followed by the sticker of the pair you want to delete. Admins can delete any pair.
Using in group chats: Once pairs are added, send the paired stickers in group chats where the bot is present. The bot will replace them with the corresponding videos.
Notes:
Make sure the bot has the necessary permissions in the group chats (e.g., delete messages).
The video files should remain accessible on Telegram's servers for the bot to send them.
You can customize the bot's behavior and messages in the bot.py script.
from email.mime import message
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, CallbackQueryHandler, Application, ContextTypes
import requests
import os
from dotenv import load_dotenv
import spotipy 
from spotipy.oauth2 import SpotifyClientCredentials
from urllib.parse import urlparse


load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET))

UrlToAdd = "http://127.0.0.1:5000/addSong"
# le fichier dans lequel on garde la liste (utile pour reprendre plus tard)

def UrlIsRight(link):
    url=urlparse(link)
    url=url.path.split("/")
    print(url)
    song_id = url[-1]
    try:
        if link.find("playlist")==-1:
            track_info = sp.track(f"https://open.spotify.com/track/{song_id}")
        else:
            track_info = sp.playlist(f"https://open.spotify.com/playlist/{song_id}")
            
        return song_id
    except spotipy.exceptions.SpotifyException as e:
        return False
    
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Welcome to the Simple Telegram Bot!"
    )
    await show_option_buttons(update, context)

async def play(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    link = context.args
    link = ' '.join(link)# Convertit la liste en une seule chaîne de caractères
    if UrlIsRight == False:
        await update.message.reply_text(f"The Spotify url is not right.")
    print(UrlIsRight)
    song_id = UrlIsRight(link)
    
    if not song_id:
        await update.message.reply_text(f"Lien non valide")
    else:
        payload = {
            "song_id" : song_id,
            "link": link,
            "author": update.message.from_user.username
        }
        print(payload)

        response = requests.post(UrlToAdd, json=payload)
        await update.message.reply_text(f"Test command executed: {response.json()}")


async def show_option_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [
        [InlineKeyboardButton("Option 1", callback_data='button_1')],
        [InlineKeyboardButton("Option 2", callback_data='button_2')],
        [InlineKeyboardButton("Option 3", callback_data='button_3')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('Please choose an option:', reply_markup=reply_markup)


async def button_selection_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(f'You selected option: {query.data.split("_")[1]}')


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        'I can respond to the following commands:\n/start - Start the bot\n/help - Get help information'
    )


def main():
    # Create the Application instance
    application = Application.builder().token(BOT_TOKEN).build()

    # Register command and message handlers
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('play', play))
    application.add_handler(CommandHandler('help', help_command))

    # Register a CallbackQueryHandler to handle button selections
    application.add_handler(CallbackQueryHandler(button_selection_handler, pattern='^button_'))

    # Start the bot
    application.run_polling()

print("Bot started...")
main()

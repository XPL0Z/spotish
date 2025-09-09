from email.mime import message
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, CallbackQueryHandler, Application, ContextTypes
import requests
import os
from dotenv import load_dotenv # type: ignore
import spotipy  # type: ignore
from spotipy.oauth2 import SpotifyClientCredentials # type: ignore
from urllib.parse import urlparse


load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET))

UrlToAdd = "http://127.0.0.1:5000/addSong"
UrlToStop = "http://127.0.0.1:5000/stop"
UrlToPause = "http://127.0.0.1:7000/pause"
UrlToResume = "http://127.0.0.1:7000/resume"
UrlToSkip = "http://127.0.0.1:5000/skip"
UrlToChangeVolume = "http://127.0.0.1:7000/volume"

songs_to_dl = []


    

        
    
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        """
        Commandes disponibles :
        /start - Ce menu
        /play <URL Spotify> - Jouer une chanson ou l’ajouter à la file d’attente
        /pause - Mettre en pause la chanson en cours
        /resume - Reprendre la lecture de la chanson en pause
        /skip - Passer la chanson en cours
        /stop - Arrêter la lecture et vider la file d’attente
        /volume <0-100> - Régler le volume
        """
    )
    
async def test(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    pass

async def play(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    link = context.args
    link = ' '.join(link)# Convertit la liste en une seule chaîne de caractères
    
    payload = {
        "link": link,
        "author": update.message.from_user.username
    }
    response = requests.post(UrlToAdd, json=payload)
    await update.message.reply_text(f"Test command executed: {response.json()}")

async def pause(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "La musique a bien été arrêtée."
    )
    requests.post(UrlToPause, json={})

async def resume(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "La zik continue !"
    )
    requests.post(UrlToResume,json={})
    
async def skip(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    r = requests.post(UrlToSkip,json={})
    await update.message.reply_text(f'Musique passé, en ce moment : {r.text}')
    
async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    requests.post(UrlToStop,json={})

async def volume(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    volume = context.args
    volume = ' '.join(volume)
    try:
        
        volume = int(volume)
    except ValueError:
        return "Erreur : le volume doit être un nombre entre 0 et 100."
    if int(float(volume)) > 100 or int(float(volume)) < 0:
        await update.message.reply_text("Intensité du volume non valide. Rappel : /volume 0 à 100")
        return
        
    payload = {
        "volume" : volume,
        "author": update.message.from_user.username
    }
    requests.post(UrlToChangeVolume,json=payload)
    await update.message.reply_text(f'Le volume est de {volume}%')
    
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
    application.add_handler(CommandHandler('test', test))
    application.add_handler(CommandHandler('play', play))
    application.add_handler(CommandHandler('pause', pause))
    application.add_handler(CommandHandler('resume', resume))
    application.add_handler(CommandHandler('skip', skip))
    application.add_handler(CommandHandler('stop', stop))
    application.add_handler(CommandHandler('volume', volume))
    application.add_handler(CommandHandler('help', help_command))

    # Register a CallbackQueryHandler to handle button selections
    application.add_handler(CallbackQueryHandler(button_selection_handler, pattern='^button_'))

    # Start the bot
    application.run_polling()

print("Bot started...")
main()

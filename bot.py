from email.mime import message
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, CallbackQueryHandler, Application, ContextTypes
from telegram.constants import ParseMode
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
ADMIN_ID = os.getenv("ADMIN_ID")
authorized_user = ADMIN_ID.split()
sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET))

UrlToAdd = "http://127.0.0.1:5000/addSong"
UrlToAddTop = "http://127.0.0.1:5000/addSongtop"
UrlToStop = "http://127.0.0.1:5000/stop"
UrlToMix = "http://127.0.0.1:5000/mix"
UrlToSkip = "http://127.0.0.1:5000/skip"
UrlToSearch = "http://127.0.0.1:5000/search"
UrlToPlayRandom = "http://127.0.1:5000/playrandom"
UrlToDownload = "http://127.0.1:5000/download"
UrlToPause = "http://127.0.0.1:7000/pause"
UrlToResume = "http://127.0.0.1:7000/resume"
UrlToChangeVolume = "http://127.0.0.1:7000/volume"
 
    
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = ("<b>🎵 Available commands:</b>\n"
            "/start - 📜 Show this menu\n"
            "/play &lt;Spotify URL&gt; - ▶️ Play a song or ➕ add it to the queue\n"
            "/playtop &lt;Spotify URL&gt; ⬆️ Add a track to the top of the queue"
            "/pause - ⏸️ Pause the current song\n"
            "/resume - 🔄 Resume the paused song\n"
            "/skip - ⏭️ Skip the current song\n"
            "/stop - 🛑 Stop playback and 🧹 clear the queue\n"
            "/volume &lt;0-100&gt; - 🔊 Adjust the volume\n"
            "/adduser &lt;username&gt; ➕ Add an authorized user (without @)\n"
            "/search &lt;track name&gt; – 🔍 Search for and play a track by name\n"
            "/mix ♾️ songs | play recommendation from history\n"
            "/download &lt;Spotify URL&gt; - 💾 Download a song or a playlist\n"
            ) 
     
    await update.message.reply_text(text=message, parse_mode=ParseMode.HTML)
    
async def test(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    pass

async def play(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    
    
    if update.message.from_user.username in authorized_user:
        link = context.args
        link = ' '.join(link)# Convert the list into a string

        payload = {
            "link": link,
            "author": update.message.from_user.username
        }
        response = requests.post(UrlToAdd, json=payload)
        await update.message.reply_text(response.json())
    else:
        await update.message.reply_text("You are not authorized ;)")
    
async def playtop(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    
    if update.message.from_user.username in authorized_user:
        link = context.args
        link = ' '.join(link)# Convert the list into a string

        payload = {
            "link": link,
            "author": update.message.from_user.username
        }
        response = requests.post(UrlToAddTop, json=payload)
        await update.message.reply_text(response.json())
    else:
        await update.message.reply_text("You are not authorized ;)")

async def pause(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    
    if update.message.from_user.username in authorized_user:
        await update.message.reply_text(
            "The music has been stopped"
        )
        requests.post(UrlToPause, json={})
    else:
        await update.message.reply_text("You are not authorized ;)")

async def resume(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    
    if update.message.from_user.username in authorized_user:
        await update.message.reply_text("The music has been resumed")
        requests.post(UrlToResume,json={})
    else:
        await update.message.reply_text("You are not authorized ;)")
    
async def skip(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    
    if update.message.from_user.username in authorized_user:
        r = requests.post(UrlToSkip,json={})
        await update.message.reply_text(f'Music skipped, Now : {r.text}')
    else:
        await update.message.reply_text("You are not authorized ;)")
        
async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message.from_user.username in authorized_user:
        requests.post(UrlToStop,json={})
    else:
        await update.message.reply_text("You are not authorized ;)")
        
async def adduser(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    
    if update.message.from_user.username == ADMIN_ID:
        user = context.args
        user = ' '.join(user)
        authorized_user.append(user)
    else:
        await update.message.reply_text("You are not admin ;)")

async def volume(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    print("Test")
    if update.message.from_user.username in authorized_user:
        try:
        # Check if there is argument
            if not context.args:
                await update.message.reply_text("Usage: /volume <0-100>")
                return

            volume = ' '.join(context.args)
            volume_int = int(float(volume))  # Change to int

            if volume_int > 100 or volume_int < 0:
                await update.message.reply_text("Volume must be between 0 and 100. Reminder: /volume 0-100")
                return

            payload = {
                "volume": volume_int
            }

            response = requests.post(UrlToChangeVolume, json=payload)

            if response.status_code == 200:
                await update.message.reply_text(f'The volume is {volume_int}%')
            else:
                await update.message.reply_text(f'Error: Server returned {response.status_code}')

        except ValueError:
            await update.message.reply_text("Please enter a valid number between 0 and 100")
        except Exception as e:
            await update.message.reply_text(f"An error occurred: {str(e)}")
            print(f"Error in volume command: {e}")
    else:
            await update.message.reply_text("You are not authorized ;)")
    
async def search(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message.from_user.username in authorized_user:
        if not context.args:
            await update.message.reply_text("Usage: /search name of the song")
            return
        search = ' '.join(context.args)
        
        payload = {
            "research" : search,
            "author": update.message.from_user.username
        }
        
        response = requests.post(UrlToSearch, json=payload)
        await update.message.reply_text(response.json())
    else: 
        await update.message.reply_text("You are not authorized ;)")

async def mix(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message.from_user.username in authorized_user:
        
        
        response = requests.post(UrlToMix, json={})
        
        await update.message.reply_text(response.json())
    else:
        await update.message.reply_text("You are not authorized") 

async def random(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    
    if update.message.from_user.username in authorized_user:
        payload = {
            "author": update.message.from_user.username
        }
        response = requests.post(UrlToPlayRandom,json=payload)
        await update.message.reply_text(response.json())
    else:
        await update.message.reply_text("You are not authorized ;)")
        
async def download(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    
    if update.message.from_user.username in authorized_user:
        link = context.args
        link = ' '.join(link)# Convert the list into a string

        payload = {
            "link": link,
            "author": update.message.from_user.username
        }
        response = requests.post(UrlToDownload,json=payload)
        await update.message.reply_text(response.json())
    else:
        await update.message.reply_text("You are not authorized ;)")
           
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





def main():
    # Create the Application instance
    application = Application.builder().token(BOT_TOKEN).build()

    # Register command and message handlers
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('test', test))
    application.add_handler(CommandHandler('play', play))
    application.add_handler(CommandHandler('playtop', playtop))
    application.add_handler(CommandHandler('pause', pause))
    application.add_handler(CommandHandler('resume', resume))
    application.add_handler(CommandHandler('skip', skip))
    application.add_handler(CommandHandler('stop', stop))
    application.add_handler(CommandHandler('volume', volume))
    application.add_handler(CommandHandler('adduser', adduser))
    application.add_handler(CommandHandler('mix', mix))
    application.add_handler(CommandHandler('search', search))
    application.add_handler(CommandHandler('random', random))
    application.add_handler(CommandHandler('download', download))
    
    # Register a CallbackQueryHandler to handle button selections
    application.add_handler(CallbackQueryHandler(button_selection_handler, pattern='^button_'))

    # Start the bot
    application.run_polling()

print("Bot started...")
print(authorized_user)
main()

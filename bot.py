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
import time
import asyncpg
import psycopg


load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
ADMIN_ID = os.getenv("ADMIN_ID")
admins = ADMIN_ID.split()
DBNAME = os.getenv("DBNAME")
DBUSER = os.getenv("DBUSER")
DBPASSWORD = os.getenv("DBPASSWORD")
DBHOST = os.geten("DBHOST")

sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET))

host_controller = os.getenv("HOST_CONTROLLER")
controller_port = os.getenv("CONTROLLER_PORT")

UrlToAdd = host_controller + controller_port + "/addSong"
UrlToAddTop = host_controller + controller_port +  "/addSongtop"
UrlToStop = host_controller + controller_port + "/stop"
UrlToMix = host_controller + controller_port + "/mix"
UrlToSkip = host_controller + controller_port + "/skip"
UrlToPrevious = host_controller + controller_port + "/previous"
UrlToSearch = host_controller + controller_port + "/search"
UrlToPlayRandom = host_controller + controller_port + "/playrandom"
UrlToDownload = host_controller + controller_port + "/download"
UrlToGetQueue = host_controller + controller_port + "/queue"
UrlToDelete = host_controller + controller_port + "/delete"
UrlToShuffle = host_controller + controller_port + "/shuffle"
UrlToPause = host_controller + controller_port + "/pause"
UrlToChangeVolume = host_controller + controller_port + "/volume"

# this function checks if a date of a user is expired and delete it, primary usage is to check if a user is authorized
async def isauthorized(username):
    conn = psycopg.connect(
        dbname=DBNAME,
        user=DBUSER,
        password=DBPASSWORD,
        host=DBHOST
    )
    cursor = conn.cursor()
    cursor.execute(
        "SELECT endat FROM authorized_users WHERE username=%s",
        (username,)
    )
    result = cursor.fetchone()
    cursor.close()
    conn.close()

    if not result:
        return False  # utilisateur non trouvé

    endat = result[0]
    if endat ==-1:
        return True  # administrateur permanent
    return time.time() < endat 

    
async def add_or_update_user(username, endat,admin:bool=False):
    conn = await asyncpg.connect(
        dbname=DBNAME,
        user=DBUSER,
        password=DBPASSWORD,
        host=DBHOST
    )

    
    await conn.execute(
    '''
    INSERT INTO authorized_users (username, endat, admin)
    VALUES ($1, $2, $3)
    ON CONFLICT (username)
    DO UPDATE SET endat = EXCLUDED.endat, admin = EXCLUDED.admin
    ''',
    username, endat, admin)

    await conn.close()

def initialise_admins():
    conn = psycopg.connect(
        dbname="spotish",
        user="postgres",
        password="1234",
        host="127.0.0.1"
    )
    cursor = conn.cursor()
    for admin in admins : 
        print(admin)
        cursor.execute(
            '''
            INSERT INTO authorized_users (username, endat, admin)
            VALUES (%s, %s, %s)
            ON CONFLICT (username)
            DO UPDATE SET endat = EXCLUDED.endat, admin = EXCLUDED.admin
            ''',
            (admin, -1, True)
        )
    print("Admins added to the DB")
    conn.commit()
    cursor.close()
    conn.close()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = ("<b>🎵 Available commands:</b>\n"
            "/start - 📜 Show this menu\n"
            "/play &lt;Spotify URL&gt; - ▶️ Play a song or ➕ add it to the queue\n"
            "/playtop &lt;Spotify URL&gt; - ⬆️ Add a track to the top of the queue\n"
            "/random - 🎲 Play a random song that is already download\n"
            "/pause - ⏸️ Pause the current song\n"
            "/resume - 🔄 Resume the paused song\n"
            "/skip - ⏭️ Skip the current song\n"
            "/previous - ⏮️ go back one song\n"
            "/stop - 🛑 Stop playback and 🧹 clear the queue\n"
            "/volume &lt;0-100&gt; - 🔊 Adjust the volume\n"
            "/adduser &lt;username&gt; &lt;duration&gt; &lt;unit&gt; - ➕ Add an authorized user \n"
            "/search &lt;track name&gt; - 🔍 Search and play a track by name\n"
            "/mix - ♾️ play recommendation from history\n"
            "/download &lt;Spotify URL&gt; - 💾 Download a song or a playlist\n"
            "/isauthorize - ❓ Checks if someone is authorize\n"
            "/queue &lt;index&gt; - 📋 Get future songs to play\n"
            "/shuffle - 🎲 randomize the queue\n"
            "/delete &lt;song_id&gt; - 🗑️ To delete a song from queue\n"
            ) 
     
    await update.message.reply_text(text=message, parse_mode=ParseMode.HTML)
    

async def play(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if await isauthorized(update.message.from_user.username) != True:
        await update.message.reply_text("You are not authorized ;)")
        return
    
    if not context.args:
        await update.message.reply_text("You must provide a link. Usage: /play <url>")
        return
    
    link = context.args
    link = ' '.join(link)# Convert the list into a string
    payload = {
        "link": link,
        "author": update.message.from_user.username
    }
    print(payload)
    response = requests.post(UrlToAdd, json=payload)
    await update.message.reply_text(response.json())

    
    
async def playtop(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if await isauthorized(update.message.from_user.username) != True:
        await update.message.reply_text("You are not authorized ;)")
        return
    
    link = context.args
    link = ' '.join(link)# Convert the list into a string
    payload = {
        "link": link,
        "author": update.message.from_user.username
    }
    response = requests.post(UrlToAddTop, json=payload)
    await update.message.reply_text(response.json())
    

async def pause(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    
    if await isauthorized(update.message.from_user.username) != True:
        await update.message.reply_text("You are not authorized ;)")
        return

    payload = {
        "author": update.message.from_user.username
    }
    response = requests.post(UrlToPause, json=payload)
    await update.message.reply_text(response.json())
    
    
async def skip(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    
    if await isauthorized(update.message.from_user.username) != True:
        await update.message.reply_text("You are not authorized ;)")
        return

    payload = {
        "author": update.message.from_user.username
    }
    
    response = requests.post(UrlToSkip,json=payload)
    await update.message.reply_text(response.json())

async def previous(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    
    if await isauthorized(update.message.from_user.username) != True:
        await update.message.reply_text("You are not authorized ;)")
        return

    payload = {
        "author": update.message.from_user.username
    }
    
    response = requests.post(UrlToPrevious,json=payload)
    await update.message.reply_text(response.json())
    
        
async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if await isauthorized(update.message.from_user.username) != True:
        await update.message.reply_text("You are not authorized ;)")
        return
    
    payload = {
        "author": update.message.from_user.username
    }
    response = requests.post(UrlToStop,json=payload)
    await update.message.reply_text(response.json())
    
async def test(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if await isauthorized(update.message.from_user.username) == True:
        await update.message.reply_text("You are authorized ;)")
    else:
        await update.message.reply_text("You are not authorized ;)")
        
async def isauthorize(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    arg = context.args
    arg = ' '.join(arg)
    arg = arg.split("@")[1]
    if len(arg) == 0:
        if await isauthorized(update.message.from_user.username) == True:
            await update.message.reply_text(f"You are @{update.message.from_user.username} and authorized ;)")
        else:
            await update.message.reply_text(f"You are @{update.message.from_user.username} and not authorized ;)")
    else:
        if await isauthorized(arg) == True:
            await update.message.reply_text(f"@{arg} is authorized ;)")
        else:
            await update.message.reply_text(f"@{arg} is not authorized ;)")
    
        
async def adduser(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    
    if update.message.from_user.username not in admins:
        await update.message.reply_text("You are not authorized ;)")
        return
    
    if len(context.args) != 3:
        await update.message.reply_text("Invalid. Usage: /adduser @alice 30 m Use s (seconds), m (minutes), or h (hours).")
        return
    
    username = context.args[0]
    username = username.split("@")[1]
    duration = abs(int(context.args[1]))
    unit = context.args[2]
    current_time = int(time.time())
    if unit == "s":
        endat = current_time + duration
        message = f"@{username} is now allowed for {duration} seconds"
    elif unit == "m":
        endat = current_time + duration * 60
        message = f"@{username} is now allowed for {duration} minutes"
    elif unit == "h":
        endat = current_time + duration * 3600
        message = f"@{username} is now allowed for {duration} hours"
    else:
        await update.message.reply_text("Invalid. Usage: /adduser @alice 30 m Use s (seconds), m (minutes), or h (hours).")
        return
    
    
    await add_or_update_user(username,endat)
    
    await update.message.reply_text(message)
    

async def volume(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if await isauthorized(update.message.from_user.username) != True:
        await update.message.reply_text("You are not authorized ;)")
        return
    
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
    
async def search(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if await isauthorized(update.message.from_user.username) != True:
        await update.message.reply_text("You are not authorized ;)")
        return
    
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
    

async def mix(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if await isauthorized(update.message.from_user.username) != True:
        await update.message.reply_text("You are not authorized ;)")
        return
    payload = {
        "author": update.message.from_user.username
    }
    response = requests.post(UrlToMix, json=payload)
    
    await update.message.reply_text(response.json())


async def random(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if await isauthorized(update.message.from_user.username) != True:
        await update.message.reply_text("You are not authorized ;)")
        return
    
    payload = {
        "author": update.message.from_user.username
    }
    response = requests.post(UrlToPlayRandom,json=payload)
    await update.message.reply_text(response.json())

        
async def download(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if await isauthorized(update.message.from_user.username) != True:
            await update.message.reply_text("You are not authorized ;)")
            return
    
        link = context.args
        link = ' '.join(link)# Convert the list into a string

        payload = {
            "link": link,
            "author": update.message.from_user.username
        }
        response = requests.post(UrlToDownload,json=payload)
        await update.message.reply_text(response.json())
    
async def queue(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if await isauthorized(update.message.from_user.username) != True:
            await update.message.reply_text("You are not authorized ;)")
            return
        
        index = context.args
        
        

        if len(index) == 0:
            
            index = 1
        else:
            if index[0] == "404":
                return await update.message.reply_text("Are you a neeerd 🤓🥸 ?")
            index = ' '.join(index)
        
        payload = {
            "index": int(index)
        }

        response = requests.post(UrlToGetQueue,json=payload)
        responsejson = response.json()
        
        message = "Index | Name | Spotify ID \n"
        if len(response.json()) > 0:
            for i in range(len(response.json())):
                message += f"{responsejson[i]['place']} {responsejson[i]['name']} {responsejson[i]['song_id']} \n"
            return await update.message.reply_text(message)
        return await update.message.reply_text("The queue is empty")
        

async def delete(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if await isauthorized(update.message.from_user.username) != True:
            await update.message.reply_text("You are not authorized ;)")
            return
        
        song_id = context.args
        song_id = ' '.join(song_id)# Convert the list into a string
        
        payload = {
            "song_id": song_id,
            "author":update.message.from_user.username
        }

        response = requests.post(UrlToDelete,json=payload)
        
        await update.message.reply_text(response.json())
        
async def shuffle(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if await isauthorized(update.message.from_user.username) != True:
            await update.message.reply_text("You are not authorized ;)")
            return

        payload = {
            "author": update.message.from_user.username
        }
        response = requests.post(UrlToShuffle,json=payload)
        
        await update.message.reply_text(response.json())
        
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
    application.add_handler(CommandHandler('help', start))
    application.add_handler(CommandHandler('test', test))
    application.add_handler(CommandHandler('play', play))
    application.add_handler(CommandHandler('playtop', playtop))
    application.add_handler(CommandHandler('pause', pause))
    application.add_handler(CommandHandler('resume', pause))
    application.add_handler(CommandHandler('skip', skip))
    application.add_handler(CommandHandler('stop', stop))
    application.add_handler(CommandHandler('volume', volume))
    application.add_handler(CommandHandler('adduser', adduser))
    application.add_handler(CommandHandler('mix', mix))
    application.add_handler(CommandHandler('search', search))
    application.add_handler(CommandHandler('random', random))
    application.add_handler(CommandHandler('download', download))
    application.add_handler(CommandHandler('isauthorize', isauthorize))
    application.add_handler(CommandHandler('queue', queue))
    application.add_handler(CommandHandler('delete', delete))
    application.add_handler(CommandHandler('shuffle', shuffle))
    application.add_handler(CommandHandler('previous', previous))
    # Register a CallbackQueryHandler to handle button selections
    application.add_handler(CallbackQueryHandler(button_selection_handler, pattern='^button_'))

    # Start the bot
    application.run_polling()

print("Bot started...")
print(admins)
# asyncio.run(initialise_admins())
initialise_admins()
main()

import vlc
import time

player = vlc.MediaPlayer('Songs/5qaEfEh1AtSdrdrByCP7qR.mp3')
# creating vlc media player object
# media_player = vlc.MediaPlayer()

# define media
# media = vlc.Media("Songs/5qaEfEh1AtSdrdrByCP7qR.mp3")

# media object
# media_player.set_media(media)

# print(vlc.State.Ended)

player.play()
print(player.get_state())
print(vlc.State.Ended)
while not player.get_state() == vlc.State.Ended:
    time.sleep(0.1)
print("fin")
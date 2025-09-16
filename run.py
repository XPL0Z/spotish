from multiprocessing import Process
import subprocess
import git  # pip install gitpython
import os 
import time


current_dir = os.getcwd() 

repo = git.Repo(current_dir)

current = repo.head.commit

repo.remotes.origin.pull()

if current != repo.head.commit:
    print("It changed")
else:
    print("You have the last version")
    
scripts = ["bot.py", "music-controller.py", "music-player.py"]


processes = []
for file in scripts:
    p = Process(target=subprocess.run, args=(["python3", file],))
    p.start()
    processes.append(p)
    time.sleep(2)

print("Tous les scripts tournent en parallèle.")

for p in processes:
    p.join()

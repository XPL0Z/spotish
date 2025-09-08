from multiprocessing import Process
import subprocess

scripts = ["bot.py", "music-player.py", "music-controller.py"]

processes = []
for s in scripts:
    p = Process(target=subprocess.run, args=(["python3", s],))
    p.start()
    processes.append(p)

print("Tous les scripts tournent en parallèle.")

for p in processes:
    p.join()

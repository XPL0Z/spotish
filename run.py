from multiprocessing import Process
import subprocess
import git  # pip install gitpython
import os
import time
from dotenv import load_dotenv

load_dotenv()

IntervalBetweenCheckForUpdate = os.getenv("INTERVAL")

# liste de tes scripts
scripts = ["bot.py", "music-controller.py", "music-player.py"]

# chemin vers ton repo (met ton chemin absolu si nécessaire)
repo_path = os.getcwd()

def start_scripts():
    """Lance tous les scripts dans des processus séparés"""
    processes = []
    for file in scripts:
        p = Process(target=subprocess.run, args=(["python3", file],))
        p.start()
        processes.append(p)
        time.sleep(1)  # léger délai pour éviter les conflits au démarrage
    return processes

def check_and_update_repo():
    """Vérifie si le repo est à jour, fait git pull si nécessaire"""
    repo = git.Repo(repo_path)
    origin = repo.remotes.origin
    origin.fetch()  # récupère les dernières infos du remote
    branch = repo.active_branch

    behind = list(repo.iter_commits(f'{branch.name}..origin/{branch.name}'))
    if behind:
        print(f"⬇️ Repo en retard de {len(behind)} commit(s). Pull en cours...")
        origin.pull()
        return True  # indique qu'on a fait un pull
    else:
        print("✅ Repo à jour")
        return False

def main_loop():
    processes = start_scripts()
    print("All scripts are running")

    try:
        while True:
            
            
            # vérifie le repo
            if check_and_update_repo():
                # si pull effectué, relance les scripts
                print("🔄 Relance des scripts après pull")
                for p in processes:
                    p.terminate()
                    p.join()
                
                processes = start_scripts()
                
            # attend 1 heure
            time.sleep(IntervalBetweenCheckForUpdate)
    except KeyboardInterrupt:
        print("Arrêt manuel, kill des scripts...")
        for p in processes:
            p.terminate()
            p.join()

if __name__ == "__main__":
    main_loop()

from multiprocessing import Process
import subprocess
import git  # pip install gitpython
import os
import time
import signal
import psutil  # pip install psutil
from dotenv import load_dotenv

load_dotenv()

IntervalBetweenCheckForUpdate = int(os.getenv("INTERVAL", 60))  # défaut 60s

# liste de tes scripts
scripts = ["bot.py", "music-controller.py", "music-player.py"]
  
# chemin vers ton repo
repo_path = os.getcwd()

class ScriptManager:
    def __init__(self):
        self.processes = {}
        
    def is_script_running(self, script_name):
        """Vérifie si un script est déjà en cours d'exécution sur le système"""
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                cmdline = proc.info['cmdline']
                if cmdline and len(cmdline) >= 2:
                    if 'python' in cmdline[0] and script_name in cmdline[1]:
                        return True
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return False
    
    def start_script(self, script_name):
        """Lance un script uniquement s'il n'est pas déjà en cours"""
        if self.is_script_running(script_name):
            print(f"⚠️  {script_name} est déjà en cours d'exécution")
            return None
            
        print(f"🚀 Lancement de {script_name}")
        p = Process(target=subprocess.run, args=(["python3", script_name],))
        p.start()
        return p
    
    def start_all_scripts(self):
        """Lance tous les scripts"""
        self.processes = {}
        for script in scripts:
            p = self.start_script(script)
            if p:
                self.processes[script] = p
            time.sleep(2)  # délai entre les lancements
        
        print(f"✅ {len(self.processes)} scripts lancés")
    
    def stop_all_scripts(self):
        """Arrête proprement tous les scripts gérés + ceux du système"""
        print("🛑 Arrêt de tous les scripts...")
        
        # Arrête les processus qu'on a lancés
        for script, p in self.processes.items():
            if p and p.is_alive():
                print(f"  Arrêt de {script}")
                p.terminate()
                try:
                    p.join(timeout=5)
                except:
                    p.kill()  # force kill si terminate échoue
        
        # Vérifie et tue les processus restants sur le système
        for script in scripts:
            self.kill_system_process(script)
            
        self.processes = {}
        print("✅ Tous les scripts arrêtés")
    
    def kill_system_process(self, script_name):
        """Force l'arrêt d'un script au niveau système"""
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                cmdline = proc.info['cmdline']
                if cmdline and len(cmdline) >= 2:
                    if 'python' in cmdline[0] and script_name in cmdline[1]:
                        print(f"  🔪 Force kill de {script_name} (PID: {proc.info['pid']})")
                        proc.kill()
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
    
    def check_scripts_health(self):
        """Vérifie si les scripts tournent encore et les relance si nécessaire"""
        for script in scripts:
            if script in self.processes:
                p = self.processes[script]
                if not p.is_alive():
                    print(f"💀 {script} s'est arrêté, relance...")
                    new_p = self.start_script(script)
                    if new_p:
                        self.processes[script] = new_p

def check_and_update_repo():
    """Vérifie et met à jour le repo si nécessaire"""
    try:
        repo = git.Repo(repo_path)
        origin = repo.remotes.origin
        origin.fetch()
        branch = repo.active_branch

        behind = list(repo.iter_commits(f'{branch.name}..origin/{branch.name}'))
        if behind:
            print(f"⬇️ Repo en retard de {len(behind)} commit(s). Pull en cours...")
            origin.pull()
            return True
        else:
            print("✅ Repo à jour")
            return False
    except Exception as e:
        print(f"❌ Erreur lors de la vérification du repo: {e}")
        return False

def main_loop():
    manager = ScriptManager()
    
    # Nettoie d'éventuels processus en cours
    manager.stop_all_scripts()
    time.sleep(3)
    
    # Lance les scripts
    manager.start_all_scripts()
    
    try:
        while True:
            # Vérifie la santé des scripts
            manager.check_scripts_health()
            
            # Vérifie le repo
            if check_and_update_repo():
                print("🔄 Redémarrage après mise à jour...")
                manager.stop_all_scripts()
                time.sleep(5)  # délai pour que tout s'arrête
                manager.start_all_scripts()
            
            time.sleep(IntervalBetweenCheckForUpdate)
            
    except KeyboardInterrupt:
        print("\n🛑 Arrêt manuel détecté")
        manager.stop_all_scripts()

def signal_handler(signum, frame):
    """Gestionnaire pour arrêt propre via signal"""
    print(f"\n🛑 Signal {signum} reçu, arrêt en cours...")
    manager = ScriptManager()
    manager.stop_all_scripts()
    exit(0)

if __name__ == "__main__":
    # Gestionnaire de signaux pour arrêt propre
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    main_loop()
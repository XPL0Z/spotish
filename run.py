from multiprocessing import Process
import subprocess
import git  # pip install gitpython
import os
import time
import signal
import psutil  # pip install psutil
from datetime import datetime, time as dt_time
from dotenv import load_dotenv

load_dotenv()

# Check hours (24h format) - add/remove hours as needed
CHECK_HOURS = [int(h.strip()) for h in os.getenv("CHECK_HOURS", "9,12,15,18,21").split(",")]
IntervalBetweenCheckForUpdate = int(os.getenv("INTERVAL", 300))  # default 5min

# list of your scripts
scripts = ["bot.py", "music-controller.py", "music-player.py"]

# path to your repo
repo_path = os.getcwd()

class ScriptManager:
    def __init__(self):
        self.processes = {}
        
    def find_script_processes(self, script_name):
        """Find ALL processes running the script (more robust detection)"""
        found_processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'exe']):
            try:
                # Check command line
                cmdline = proc.info['cmdline']
                if cmdline:
                    cmdline_str = ' '.join(cmdline)
                    if script_name in cmdline_str and ('python' in cmdline_str or 'py' in proc.info['name']):
                        found_processes.append(proc)
                        continue
                
                # Check executable path
                exe = proc.info.get('exe', '')
                if exe and script_name in exe:
                    found_processes.append(proc)
                    
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
        return found_processes
    
    def is_script_running(self, script_name):
        """Check if a script is already running on the system"""
        return len(self.find_script_processes(script_name)) > 0
    
    def start_script(self, script_name):
        """Start a script only if it's not already running"""
        if self.is_script_running(script_name):
            print(f"⚠️  {script_name} is already running")
            return None
            
        print(f"🚀 Starting {script_name}")
        p = Process(target=subprocess.run, args=(["python3", script_name],))
        p.start()
        return p
    
    def start_all_scripts(self):
        """Start all scripts"""
        self.processes = {}
        for script in scripts:
            p = self.start_script(script)
            if p:
                self.processes[script] = p
            time.sleep(2)  # delay between launches
        
        print(f"✅ {len(self.processes)} scripts started")
    
    def stop_all_scripts(self):
        """Properly stop all scripts managed + system ones"""
        print("🛑 Stopping all scripts...")
        
        # Stop processes we launched
        for script, p in self.processes.items():
            if p and p.is_alive():
                print(f"  Stopping managed {script}")
                p.terminate()
                try:
                    p.join(timeout=5)
                except:
                    print(f"  Force killing managed {script}")
                    p.kill()
        
        # Find and kill ALL system processes
        for script in scripts:
            self.kill_all_script_processes(script)
            
        self.processes = {}
        print("✅ All scripts stopped")
    
    def kill_all_script_processes(self, script_name):
        """Force stop ALL instances of a script at system level"""
        processes = self.find_script_processes(script_name)
        for proc in processes:
            try:
                print(f"  🔪 Force killing {script_name} (PID: {proc.pid})")
                proc.kill()
                proc.wait(timeout=3)  # wait for process to die
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.TimeoutExpired):
                try:
                    # Try SIGTERM first, then SIGKILL
                    proc.send_signal(signal.SIGTERM)
                    time.sleep(1)
                    if proc.is_running():
                        proc.send_signal(signal.SIGKILL)
                except:
                    pass
    
    def check_scripts_health(self):
        """Check if scripts are still running and restart them if necessary"""
        for script in scripts:
            if script in self.processes:
                p = self.processes[script]
                if not p.is_alive():
                    print(f"💀 {script} has stopped, restarting...")
                    new_p = self.start_script(script)
                    if new_p:
                        self.processes[script] = new_p
    
    def debug_running_scripts(self):
        """Debug: show all running script processes"""
        print("\n🔍 Debug - Current running processes:")
        for script in scripts:
            processes = self.find_script_processes(script)
            if processes:
                for proc in processes:
                    try:
                        print(f"  {script}: PID {proc.pid} - {proc.cmdline()}")
                    except:
                        print(f"  {script}: PID {proc.pid} - <cannot read cmdline>")
            else:
                print(f"  {script}: Not running")
        print()

def check_and_update_repo():
    """Check and update repo if necessary"""
    try:
        repo = git.Repo(repo_path)
        origin = repo.remotes.origin
        origin.fetch()
        branch = repo.active_branch

        behind = list(repo.iter_commits(f'{branch.name}..origin/{branch.name}'))
        if behind:
            print(f"⬇️ Repo behind by {len(behind)} commit(s). Pulling...")
            origin.pull()
            return True
        else:
            print("✅ Repo up to date")
            return False
    except Exception as e:
        print(f"❌ Error checking repo: {e}")
        return False

def should_check_now():
    """Check if current time matches one of the check hours"""
    current_hour = datetime.now().hour
    return current_hour in CHECK_HOURS

def wait_until_next_check():
    """Wait until the next scheduled check time"""
    current_time = datetime.now()
    current_hour = current_time.hour
    
    # Find next check hour
    next_check_hour = None
    for hour in sorted(CHECK_HOURS):
        if hour > current_hour:
            next_check_hour = hour
            break
    
    # If no hour found today, use first hour of tomorrow
    if next_check_hour is None:
        next_check_hour = min(CHECK_HOURS)
        next_check_time = datetime.combine(
            current_time.date().replace(day=current_time.day + 1),
            dt_time(next_check_hour, 0)
        )
    else:
        next_check_time = datetime.combine(
            current_time.date(),
            dt_time(next_check_hour, 0)
        )
    
    wait_seconds = (next_check_time - current_time).total_seconds()
    print(f"⏰ Next check at {next_check_time.strftime('%H:%M')} (in {wait_seconds/3600:.1f}h)")
    return wait_seconds

def main_loop():
    manager = ScriptManager()
    
    print(f"🕐 Scheduled checks at: {', '.join([f'{h}:00' for h in sorted(CHECK_HOURS)])}")
    
    # Clean any existing processes
    manager.debug_running_scripts()  # debug before cleanup
    manager.stop_all_scripts()
    time.sleep(3)
    
    # Check and update repo at startup
    print("🚀 Checking git at startup...")
    startup_updated = check_and_update_repo()
    if startup_updated:
        print("🔄 Repository updated at startup")
    
    # Start scripts
    manager.start_all_scripts()
    
    last_check_time = None
    
    try:
        while True:
            current_time = datetime.now()
            
            # Check scripts health periodically (every interval)
            manager.check_scripts_health()
            
            # Check repo only at scheduled hours
            if should_check_now():
                current_hour = current_time.hour
                
                # Avoid checking multiple times in the same hour
                if last_check_time is None or last_check_time.hour != current_hour:
                    print(f"\n🕐 Scheduled check at {current_time.strftime('%H:%M')}")
                    
                    if check_and_update_repo():
                        print("🔄 Restarting after update...")
                        manager.debug_running_scripts()  # debug before restart
                        manager.stop_all_scripts()
                        time.sleep(5)  # wait for everything to stop
                        manager.start_all_scripts()
                    
                    last_check_time = current_time
                    
                    # Wait until next scheduled check
                    wait_seconds = wait_until_next_check()
                    if wait_seconds > IntervalBetweenCheckForUpdate:
                        print(f"💤 Sleeping until next check...")
                        time.sleep(wait_seconds)
                        continue
            
            time.sleep(IntervalBetweenCheckForUpdate)
            
    except KeyboardInterrupt:
        print("\n🛑 Manual stop detected")
        manager.debug_running_scripts()  # debug before cleanup
        manager.stop_all_scripts()

def signal_handler(signum, frame):
    """Handler for clean stop via signal"""
    print(f"\n🛑 Signal {signum} received, stopping...")
    manager = ScriptManager()
    manager.stop_all_scripts()
    exit(0)

if __name__ == "__main__":
    # Signal handlers for clean stop
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    main_loop()
import subprocess
import sys
import time
import os

# Set environment variables
env = os.environ.copy()
env["OTREE_ADMIN_PASSWORD"] = "admin"
env["SECRET_KEY"] = "dev-secret-key"
env["PYTHONPATH"] = r"C:\Users\tukum\Downloads\carbonsim-online;" + env.get("PYTHONPATH", "")

# Start oTree devserver
log_path = r"C:\Users\tukum\Downloads\carbonsim-online\platform\otree_server.log"
with open(log_path, "w") as log:
    proc = subprocess.Popen(
        ["otree", "devserver", "0.0.0.0:8000"],
        cwd=r"C:\Users\tukum\Downloads\carbonsim-online\platform",
        env=env,
        stdout=log,
        stderr=subprocess.STDOUT,
    )
    # Write PID to a file so we can find it later
    with open(r"C:\Users\tukum\Downloads\carbonsim-online\platform\otree_server.pid", "w") as pid_file:
        pid_file.write(str(proc.pid))
    # Wait a bit for startup, then exit
    time.sleep(15)
    # Check if process is still running
    if proc.poll() is None:
        print(f"Server started (PID {proc.pid}). Check {log_path} for details.")
    else:
        print(f"Server exited with code {proc.returncode}. Check {log_path} for details.")
        sys.exit(1)

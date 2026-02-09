import os
import json
import platform
import subprocess
import sys
import threading
import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
from PIL import Image, ImageTk
import hashlib
import urllib.request
import psutil
import zipfile

EMBEDDED_CONFIG = {
  "repo_url": "https://github.com/gretaisright/erindor-client.git",
  "branch": "master",
  "binaries_base_url": "https://github.com/gretaisright/erindor-client/releases/download/1.0",
  "git_zip_url": "https://github.com/gretaisright/otclient-erindor-launcher/releases/download/git/git.zip"
}

# ======================================================
#  PATHS / CONFIG
# ======================================================

def get_real_base_dir() -> Path:
    if getattr(sys, 'frozen', False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent

BASE_DIR = get_real_base_dir()
GAME_DIR = BASE_DIR / "game_data"
GIT_DIR = BASE_DIR / "git" / "git"
GIT_EXE = GIT_DIR / "bin" / "git.exe"
GIT_ZIP_URL = "https://github.com/gretaisright/otclient-erindor-launcher/releases/tag/1.0"
GIT_ZIP_DIR = BASE_DIR / "git"
GIT_ZIP_PATH = GIT_ZIP_DIR / "git.zip"
CONFIG_FILE = BASE_DIR / "launcher.json"
IMAGE_FILE = BASE_DIR / "game_data" / "launcher.png"
CREATE_NO_WINDOW = subprocess.CREATE_NO_WINDOW

# ======================================================
#  CONFIG
# ======================================================

def load_launcher_config():
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)

    # fallback to embedded config
    return EMBEDDED_CONFIG.copy()

def get_asset_path(name: str) -> Path:
    base = get_real_base_dir()
    path = base / name
    return path if path.exists() else None


def git_env():
    env = os.environ.copy()

    git_bin = str(GIT_DIR / "bin")
    git_mingw = str(GIT_DIR / "mingw64" / "bin")

    env["PATH"] = git_bin + os.pathsep + git_mingw + os.pathsep + env.get("PATH", "")

    return env

# ======================================================
#  SYSTEM CHECK
# ======================================================

def is_64bit_windows():
    return platform.machine().endswith("64")

def has_directx():
    system32 = os.path.join(os.environ.get("SystemRoot", "C:\\Windows"), "System32")
    return any(os.path.exists(os.path.join(system32, dll)) for dll in ("d3d11.dll", "d3d9.dll"))

def sha256_file(path: Path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()

def is_client_running(exe_name: str) -> bool:
    exe_name = exe_name.lower()

    for proc in psutil.process_iter(["name", "exe"]):
        try:
            name = proc.info["name"]
            exe = proc.info["exe"]

            if name and name.lower() == exe_name:
                return True

            if exe and os.path.basename(exe).lower() == exe_name:
                return True

        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    return False

def any_client_running():
    candidates = [
        "_gl_x64.exe",
        "_dx_x64.exe",
        "_gl.exe",
        "_dx.exe"
    ]

    for exe in candidates:
        if is_client_running(exe):
            return True

    return False

# ======================================================
#  CLIENT SELECTION (IMPORTANTE)
# ======================================================

def ensure_client_binaries(cfg, client_key):
    binaries_file = GAME_DIR / "binaries.json"
    if not binaries_file.exists():
        raise RuntimeError("binaries.json not found in game_data")

    data = json.loads(binaries_file.read_text(encoding="utf-8"))

    if client_key not in data["clients"]:
        raise RuntimeError(
            f"Client '{client_key}' not found in binaries.json"
        )

    info = data["clients"][client_key]
    base_url = cfg["binaries_base_url"]

    exe_path = GAME_DIR / info["file"]

    # já existe e hash confere?
    if exe_path.exists():
        local_hash = sha256_file(exe_path)
        if local_hash.lower() == info["sha256"].lower():
            return exe_path

    # precisa baixar
    url = f"{base_url}/{info['file']}"
    print(f"[BIN] Downloading {info['file']}")

    urllib.request.urlretrieve(url, exe_path)

    if sha256_file(exe_path).lower() != info["sha256"].lower():
        raise RuntimeError(f"Checksum mismatch for {info['file']}")

    return exe_path

def find_best_client(binaries):
    """
    binaries = dict vindo do binaries.json["clients"]
    """

    bit64 = is_64bit_windows()
    directx = has_directx()

    # prioridade máxima
    if bit64 and "gl_x64" in binaries:
        return "gl_x64", "OpenGL 64-bit"

    if bit64 and directx and "dx_x64" in binaries:
        return "dx_x64", "DirectX 64-bit"

    # fallback 32 bits
    if "gl_x86" in binaries:
        return "gl_x86", "OpenGL 32-bit"

    if directx and "dx_x86" in binaries:
        return "dx_x86", "DirectX 32-bit"

    # 🔥 fallback FINAL — obrigatório existir
    if "gl_x64" in binaries:
        return "gl_x64", "OpenGL 64-bit (fallback)"

    raise RuntimeError("Nenhum cliente compatível encontrado em binaries.json")


# ======================================================
#  UI HELPERS
# ======================================================

def show_error(title, msg):
    tk.Tk().withdraw()
    messagebox.showerror(title, msg)

# ======================================================
#  GIT LOGIC
# ======================================================


def run_git(cmd, cwd, on_output):
    proc = subprocess.Popen(
        cmd,
        cwd=cwd,
        env=git_env(),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
        creationflags=CREATE_NO_WINDOW
    )

    for line in proc.stdout:
        on_output(line.rstrip())

    proc.wait()
    if proc.returncode != 0:
        raise subprocess.CalledProcessError(proc.returncode, cmd)

def update_game_data(cfg, on_status, on_progress):
    repo = cfg["repo_url"]
    branch = cfg["branch"]

    ensure_git_available(cfg, on_status)

    def parse_progress(line):
        on_status(line)
        for key in ("Receiving objects", "Resolving deltas", "Updating files"):
            if key in line and "%" in line:
                try:
                    on_progress(int(line.split("%")[0].split()[-1]))
                except:
                    pass

    if not (GAME_DIR / ".git").exists():
        on_status("Cloning repository...")
        run_git(
            [str(GIT_EXE), "clone", "--progress", "--branch", branch, repo, str(GAME_DIR)],
            BASE_DIR,
            parse_progress
        )
    else:
        on_status("Updating repository...")
        run_git([str(GIT_EXE), "fetch", "--progress"], GAME_DIR, parse_progress)
        run_git([str(GIT_EXE), "reset", "--hard", f"origin/{branch}"], GAME_DIR, parse_progress)
        run_git([str(GIT_EXE), "clean", "-fd"], GAME_DIR, parse_progress)

    on_progress(100)
    on_status("Update complete.")

def ensure_git_available(cfg, on_status=None):
    if GIT_EXE.exists():
        return

    git_zip_url = cfg.get("git_zip_url", GIT_ZIP_URL)

    if on_status:
        on_status("Downloading Git...")

    GIT_ZIP_DIR.mkdir(parents=True, exist_ok=True)
    urllib.request.urlretrieve(git_zip_url, GIT_ZIP_PATH)

    if on_status:
        on_status("Extracting Git...")

    with zipfile.ZipFile(GIT_ZIP_PATH, "r") as zf:
        zf.extractall(GIT_ZIP_DIR)

    try:
        GIT_ZIP_PATH.unlink()
    except OSError:
        pass

    if not GIT_EXE.exists():
        raise RuntimeError("git.exe not found after extracting git.zip")

# ======================================================
#  UI WINDOW
# ======================================================

def show_update_window(cfg):
    win = tk.Tk()
    win.overrideredirect(True)
    win.configure(bg="black")

    w, h = 600, 340
    x = (win.winfo_screenwidth() - w) // 2
    y = (win.winfo_screenheight() - h) // 2
    win.geometry(f"{w}x{h}+{x}+{y}")

    # Background image
    if IMAGE_FILE.exists():
        img = Image.open(IMAGE_FILE).resize((w, h))
        bg = ImageTk.PhotoImage(img)
        lbl = tk.Label(win, image=bg, bd=0)
        lbl.image = bg
        lbl.place(x=0, y=0, relwidth=1, relheight=1)

    # Bottom bar (faixa preta)
    bottom = tk.Frame(win, bg="black", height=70)
    bottom.pack(side="bottom", fill="x")
    bottom.pack_propagate(False)

    status = tk.Label(
        bottom,
        text="Starting update...",
        fg="white",
        bg="black",
        font=("Segoe UI", 11),
        anchor="w"
    )
    status.pack(fill="x", padx=20, pady=(10, 4))

    bar = ttk.Progressbar(
        bottom,
        mode="determinate"
    )
    bar.pack(fill="x", padx=20, pady=(0, 12))

    def set_status(t):
        status.config(text=t)
        win.update_idletasks()

    def set_progress(p):
        bar["value"] = p
        win.update_idletasks()

    def worker():
        try:
            if any_client_running():
                set_status("Client already running. Launching another instance...")
                launch_game(cfg)
                win.destroy()
                return
            update_game_data(cfg, set_status, set_progress)

            set_status("Launching client...")
            launch_game(cfg)
            win.destroy()

        except Exception as e:
            show_error("Launcher error", str(e))
            win.destroy()

    threading.Thread(target=worker, daemon=True).start()
    win.mainloop()

# ======================================================
#  LAUNCH
# ======================================================

def launch_game(cfg):
    binaries_file = GAME_DIR / "binaries.json"
    data = json.loads(binaries_file.read_text(encoding="utf-8"))

    client_key, label = find_best_client(data["clients"])
    print(f"[LAUNCHER] Selected client: {label}")

    exe_path = ensure_client_binaries(cfg, client_key)

    subprocess.Popen(
        [str(exe_path), "--from-launcher"],
        cwd=str(GAME_DIR),
        creationflags=CREATE_NO_WINDOW
    )

# ======================================================
#  MAIN
# ======================================================

def main():
    try:
        cfg = load_launcher_config()
    except Exception as e:
        show_error("Launcher error", str(e))
        return

    show_update_window(cfg)

if __name__ == "__main__":
    main()

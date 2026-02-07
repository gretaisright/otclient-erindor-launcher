import os
import shutil
import subprocess
from pathlib import Path

# ===================================================
# CONFIGURAÇÕES PRINCIPAIS
# ===================================================

def get_root_dir(levels_up: int) -> Path:
    base = Path(__file__).resolve().parent
    for _ in range(levels_up):
        if base.parent == base:
            break
        base = base.parent
    return base

ROOT_DIR = get_root_dir(1)

# Pasta do launcher (onde ficará o .exe final)
LAUNCHER_DIR = ROOT_DIR / "launcher"

SCRIPT_NAME = LAUNCHER_DIR / "launcher.py"
OUTPUT_NAME = "launcher.exe"

ICON_PATH = LAUNCHER_DIR / "launcher.ico"
BACKGROUND_PATH = LAUNCHER_DIR / "launcher.png"
CONFIG_PATH = LAUNCHER_DIR / "launcher.json"

# Opções de build
NOCONSOLE = True
CLEAN_BUILD = True

# ===================================================
# FUNÇÃO PRINCIPAL
# ===================================================
def main():
    base = ROOT_DIR
    dist_dir = base / "dist"
    build_dir = base / "build"
    spec_file = base / "launcher.spec"

    if not SCRIPT_NAME.exists():
        print(f"❌ Script {SCRIPT_NAME} não encontrado.")
        return

    cmd = [
        "pyinstaller",
        "--onefile",
        f"--name={OUTPUT_NAME.replace('.exe', '')}"
    ]

    if NOCONSOLE:
        cmd.append("--noconsole")

    if ICON_PATH.exists():
        cmd.append(f"--icon={ICON_PATH}")
    else:
        print(f"⚠️ Ícone {ICON_PATH} não encontrado.")

    if BACKGROUND_PATH.exists():
        cmd.append(f"--add-data={BACKGROUND_PATH};.")
    else:
        print(f"⚠️ Imagem {BACKGROUND_PATH} não encontrada.")

    if CONFIG_PATH.exists():
        cmd.append(f"--add-data={CONFIG_PATH};.")
    else:
        print(f"⚠️ Config {CONFIG_PATH} não encontrada.")

    cmd.append(str(SCRIPT_NAME))

    print("🔧 Gerando executável via PyInstaller...")
    code = subprocess.call(cmd)
    if code != 0:
        print("❌ Erro ao gerar executável.")
        return

    exe_file = dist_dir / OUTPUT_NAME
    if not exe_file.exists():
        print("❌ Executável não encontrado após build.")
        return

    # 👉 MOVE O EXE PARA A PASTA DO LAUNCHER
    target_exe = LAUNCHER_DIR / OUTPUT_NAME
    shutil.move(exe_file, target_exe)

    print(f"✅ Executável criado em: {target_exe}")

    # Limpeza
    if CLEAN_BUILD:
        for folder in (dist_dir, build_dir):
            if folder.exists():
                shutil.rmtree(folder)
        if spec_file.exists():
            spec_file.unlink()
        print("🧹 Limpeza concluída.")

if __name__ == "__main__":
    main()

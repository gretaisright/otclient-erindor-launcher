import shutil
import subprocess
from pathlib import Path

# ===================================================
# CONFIGURACOES PRINCIPAIS
# ===================================================

def get_root_dir(levels_up: int) -> Path:
    base = Path(__file__).resolve().parent
    for _ in range(levels_up):
        if base.parent == base:
            break
        base = base.parent
    return base

ROOT_DIR = get_root_dir(1)
TOOLS_DIR = ROOT_DIR / "launcher"

SCRIPT_NAME = TOOLS_DIR / "binaries.py"
OUTPUT_NAME = "binaries.exe"

ICON_PATH = TOOLS_DIR / "launcher.ico"

# Opcoes de build
NOCONSOLE = False
CLEAN_BUILD = True

# ===================================================
# FUNCAO PRINCIPAL
# ===================================================
def main() -> int:
    base = ROOT_DIR
    dist_dir = base / "dist"
    build_dir = base / "build"
    spec_file = base / "binaries.spec"

    if not SCRIPT_NAME.exists():
        print(f"Script nao encontrado: {SCRIPT_NAME}")
        return 1

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
        print(f"⚠️ Icone {ICON_PATH} nao encontrado.")

    cmd.append(str(SCRIPT_NAME))

    print("🔧 Gerando executavel via PyInstaller...")
    code = subprocess.call(cmd)
    if code != 0:
        print("❌ Erro ao gerar executavel.")
        return code

    exe_file = dist_dir / OUTPUT_NAME
    if not exe_file.exists():
        print("❌ Executavel nao encontrado apos build.")
        return 1

    target_exe = TOOLS_DIR / OUTPUT_NAME
    shutil.move(exe_file, target_exe)

    print(f"✅ Executavel criado em: {target_exe}")

    if CLEAN_BUILD:
        for folder in (dist_dir, build_dir):
            if folder.exists():
                shutil.rmtree(folder)
        if spec_file.exists():
            spec_file.unlink()
        print("🧹 Limpeza concluida.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

import argparse
import hashlib
import json
from pathlib import Path

EXPECTED_BINARIES = [
    ("gl_x64", "_gl_x64.exe"),
    ("dx_x64", "_dx_x64.exe"),
    ("gl_x86", "_gl.exe"),
    ("dx_x86", "_dx.exe"),
]


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def build_binaries_json(target_dir: Path, output_path: Path) -> int:
    data = {"clients": {}}

    for key, filename in EXPECTED_BINARIES:
        file_path = target_dir / filename
        if file_path.exists():
            data["clients"][key] = {
                "file": filename,
                "sha256": sha256_file(file_path),
            }

    if not data["clients"]:
        print("Nenhum binario esperado foi encontrado na pasta informada.")
        return 1

    output_path.write_text(
        json.dumps(data, indent=2, ensure_ascii=True),
        encoding="utf-8",
    )

    print(f"binaries.json gerado em: {output_path}")
    for key, filename in EXPECTED_BINARIES:
        if key in data["clients"]:
            print(f"- {filename}: OK")
        else:
            print(f"- {filename}: NAO ENCONTRADO")

    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Gera binaries.json com checksum dos binarios do OTClient."
    )
    parser.add_argument(
        "--dir",
        default=str(Path(__file__).resolve().parent),
        help="Pasta onde estao os binarios (padrao: pasta do script)",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Caminho do binaries.json (padrao: <dir>/binaries.json)",
    )

    args = parser.parse_args()
    target_dir = Path(args.dir).resolve()
    if not target_dir.exists():
        print(f"Pasta nao encontrada: {target_dir}")
        return 1

    output_path = Path(args.output).resolve() if args.output else target_dir / "binaries.json"
    return build_binaries_json(target_dir, output_path)


if __name__ == "__main__":
    raise SystemExit(main())

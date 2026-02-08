# launcher_otclient_git

Launcher para OTClient com update via Git. O executavel baixa um pacote de Git embutido (quando necessario), clona/atualiza o repositorio de game data e baixa os binarios do client conforme o hash.

## Para usuarios (como preparar e distribuir)

1) Suba seus arquivos do client (encryptados ou normais) em um repositorio Git publico e na branch definida no `launcher.json`.
   - No exemplo estamos usando o repositorio `.github`.
2) Gere o `binaries.json` na mesma pasta dos binarios e envie junto no repo.
   - Os binarios (_gl_x64.exe, _dx_x64.exe, _gl.exe, _dx.exe) devem ser publicados no GitHub Releases.
   - O link usado no `launcher.json` e o base da tag do release (sem o nome do arquivo), por exemplo:
     `https://github.com/JPClient/.github/releases/download/JPClient`
   - O launcher monta o link final somando o nome do arquivo do `binaries.json`.
3) Empacote o launcher para distribuir:
   - Crie uma pasta com o nome do servidor (ex: `MeuServidor/`).
   - Copie para dentro dessa pasta:
     - `launcher.exe` renomeado para `servidor_launcher.exe`
     - `launcher.json`
     - `launcher.png`
   - Compacte essa pasta em um `.zip` e envie para os jogadores.

O launcher vai manter o repositorio atualizado automaticamente a partir do `repo_url`.

lembre de subir os binários do json no mesmo link de release , nesse caso, https://github.com/JPClient/.github/releases/download/JPClient

## Protecao e comportamento

- O launcher so atualiza e apaga arquivos quando nao existe nenhuma instancia do client aberta.
- Se o Git nao existir localmente, ele baixa o `git.zip` definido no `launcher.json` e extrai em `launcher/git/`.

## Estrutura do repositorio

- `README.md`: documentacao do projeto.
- `launcher/launcher.py`: codigo do launcher (UI + update + download de binarios).
- `launcher/launcher.json`: configuracao do launcher (repositorio, branch, URLs de download).
- `launcher/launcher_build.py`: script de build com PyInstaller para gerar `launcher.exe`.
- `launcher/binaries.py`: gera `binaries.json` com checksum dos binarios.
- `launcher/binaries_build.py`: script de build do utilitario `binaries.exe`.
- `launcher/launcher.png`: imagem do launcher (fundo da janela).
- `launcher/launcher.exe`: binario gerado (build local).

Pastas geradas em runtime:
- `launcher/game_data/`: destino do repositorio clonado (game data + `binaries.json`).
- `launcher/git/`: destino do Git embutido (zip extraido em `launcher/git/git/...`).

## Configuracao (`launcher/launcher.json`)

Exemplo:

```
{
  "repo_url": "https://github.com/JPClient/.github.git",
  "branch": "JPClient",
  "binaries_base_url": "https://github.com/JPClient/.github/releases/download/JPClient",
  "git_zip_url": "https://github.com/Juanzitooh/launcher_otclient_git/releases/download/git/git.zip"
}
```

- `repo_url`: repo Git que contem o game data (no exemplo, `.github`). Ele deve ser publico para que os jogadores consigam baixar.
- `branch`: branch do repo a ser usada no clone/reset.
- `binaries_base_url`: base URL do release onde os binarios estao publicados (sem o nome do arquivo). O launcher concatena com o `file` de cada entrada do `binaries.json`.
- `git_zip_url`: pacote do Git embutido. O zip deve conter a pasta `git/` na raiz, com `git/bin/git.exe` dentro.

## binaries.json (esperado)

O launcher procura estes nomes exatos:
- `_gl_x64.exe`
- `_dx_x64.exe`
- `_gl.exe`
- `_dx.exe`

O arquivo `binaries.json` deve ter este formato:

```
{
  "clients": {
    "gl_x64": { "file": "_gl_x64.exe", "sha256": "..." },
    "dx_x64": { "file": "_dx_x64.exe", "sha256": "..." },
    "gl_x86": { "file": "_gl.exe", "sha256": "..." },
    "dx_x86": { "file": "_dx.exe", "sha256": "..." }
  }
}
```

Para gerar automaticamente:

```
python launcher/binaries.py --dir CAMINHO_DOS_BINARIOS
```

## Compilacao para Windows (PyInstaller)

Requisitos:
- Python 3.10+ (recomendado)
- `pip install -r requirements.txt`

Build do launcher:

```
python launcher/launcher_build.py
```

Build do utilitario de binaries:

```
python launcher/binaries_build.py
```

## Dependencias

- `Pillow`: carrega o background.
- `psutil`: detecta processo do client em execucao.
- `pyinstaller`: build dos executaveis.

## Links

- Git embutido: `https://github.com/Juanzitooh/launcher_otclient_git/releases/download/git/git.zip`

//

launcher_otclient_git

Launcher for OTClient with update via Git.
The executable downloads an embedded Git package (when necessary), clones/updates the game data repository, and downloads the client binaries according to the hash.

For users (how to prepare and distribute)

Upload your client files (encrypted or normal) to a public Git repository and to the branch defined in launcher.json.

In the example we are using the .github repository.

Generate the binaries.json in the same folder as the binaries and upload it together in the repo.

The binaries (_gl_x64.exe, _dx_x64.exe, _gl.exe, _dx.exe) must be published in GitHub Releases.

The link used in launcher.json is the base of the release tag (without the file name), for example:
https://github.com/JPClient/.github/releases/download/JPClient

The launcher builds the final link by appending the file name from binaries.json.

Package the launcher for distribution:

Create a folder with the server name (e.g. MyServer/).

Copy into this folder:

launcher.exe renamed to server_launcher.exe

launcher.json

launcher.png

Zip this folder into a .zip and send it to the players.

The launcher will automatically keep the repository updated based on repo_url.

Remember to upload the binaries listed in the json to the same release link, in this case:
https://github.com/JPClient/.github/releases/download/JPClient

Protection and behavior

The launcher only updates and deletes files when no client instance is running.

If Git does not exist locally, it downloads the git.zip defined in launcher.json and extracts it to launcher/git/.

Repository structure

README.md: project documentation.

launcher/launcher.py: launcher code (UI + update + binary download).

launcher/launcher.json: launcher configuration (repository, branch, download URLs).

launcher/launcher_build.py: build script with PyInstaller to generate launcher.exe.

launcher/binaries.py: generates binaries.json with checksum of the binaries.

launcher/binaries_build.py: build script for the binaries.exe utility.

launcher/launcher.png: launcher image (window background).

launcher/launcher.exe: generated binary (local build).

Folders generated at runtime:

launcher/game_data/: destination of the cloned repository (game data + binaries.json).

launcher/git/: destination of the embedded Git (zip extracted into launcher/git/git/...).

Configuration (launcher/launcher.json)

Example:

{
  "repo_url": "https://github.com/JPClient/.github.git",
  "branch": "JPClient",
  "binaries_base_url": "https://github.com/JPClient/.github/releases/download/JPClient",
  "git_zip_url": "https://github.com/Juanzitooh/launcher_otclient_git/releases/download/git/git.zip"
}


repo_url: Git repo that contains the game data (in the example, .github). It must be public so players can download it.

branch: repo branch to be used for clone/reset.

binaries_base_url: base URL of the release where the binaries are published (without the file name). The launcher concatenates this with the file field from each entry in binaries.json.

git_zip_url: embedded Git package. The zip must contain a git/ folder at the root, with git/bin/git.exe inside.

binaries.json (expected)

The launcher looks for these exact names:

_gl_x64.exe

_dx_x64.exe

_gl.exe

_dx.exe

The binaries.json file must have this format:

{
  "clients": {
    "gl_x64": { "file": "_gl_x64.exe", "sha256": "..." },
    "dx_x64": { "file": "_dx_x64.exe", "sha256": "..." },
    "gl_x86": { "file": "_gl.exe", "sha256": "..." },
    "dx_x86": { "file": "_dx.exe", "sha256": "..." }
  }
}


To generate it automatically:

python launcher/binaries.py --dir PATH_TO_BINARIES

Windows compilation (PyInstaller)

Requirements:

Python 3.10+ (recommended)

pip install -r requirements.txt

Launcher build:

python launcher/launcher_build.py


Binaries utility build:

python launcher/binaries_build.py

Dependencies

Pillow: loads the background.

psutil: detects client process running.

pyinstaller: builds the executables.

Links

Embedded Git:
https://github.com/Juanzitooh/launcher_otclient_git/releases/download/git/git.zip
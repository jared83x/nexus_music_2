# Nexus Music 2.0

Reproductor de música local estilo Spotify creado con Python + Flet.

## Incluye

- Inicio estilo Spotify
- Biblioteca
- Búsqueda
- Favoritos
- Playlists con SQLite
- Añadir canciones a playlists
- Historial
- Cola de reproducción
- Anterior / siguiente
- Shuffle
- Repeat
- Control de volumen
- Barra de progreso
- Carátulas locales
- Metadatos mediante Mutagen
- Escaneo automático de `music/`

## Instalación

Python 3.10 o superior:

```bash
python -m venv .venv
```

Windows:
```bash
.venv\Scripts\activate
```

Linux/macOS:
```bash
source .venv/bin/activate
```

Instala:

```bash
pip install -r requirements.txt
```

Ejecuta:

```bash
python main.py
```

Coloca la música dentro de:

```text
music/
```

Puedes colocar `cover.jpg`, `cover.png` o `folder.jpg` junto a los archivos de un álbum.

La base de datos se crea automáticamente en `data/music.db`.

## Empaquetar como ejecutable

Instala PyInstaller:

```bash
pip install pyinstaller
```

Windows:

```bash
pyinstaller --noconfirm --windowed --name NexusMusic --add-data "music;music" --add-data "assets;assets" main.py
```

Linux/macOS cambia `;` por `:` en `--add-data`.

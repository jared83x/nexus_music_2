from mutagen import File as AudioFile
from app.config import MUSIC_DIR, SUPPORTED

class Library:
    def __init__(self, db):
        self.db=db

    def scan(self):
        count=0
        for p in MUSIC_DIR.rglob("*"):
            if not p.is_file() or p.suffix.lower() not in SUPPORTED:
                continue
            try:
                m=AudioFile(p, easy=True)
                def tag(name, fallback):
                    v=m.get(name) if m else None
                    if isinstance(v,list):
                        v=v[0] if v else None
                    return str(v).strip() if v else fallback

                duration=0
                if m and getattr(m,"info",None):
                    duration=float(getattr(m.info,"length",0) or 0)

                cover=None
                for n in ("cover.jpg","cover.jpeg","cover.png","folder.jpg","folder.jpeg","folder.png"):
                    cp=p.parent/n
                    if cp.exists():
                        cover=str(cp.resolve())
                        break

                self.db.upsert_track({
                    "title":tag("title",p.stem),
                    "artist":tag("artist","Artista desconocido"),
                    "album":tag("album","Álbum desconocido"),
                    "genre":tag("genre","Desconocido"),
                    "path":str(p.resolve()),
                    "cover":cover,
                    "duration":duration
                })
                count+=1
            except Exception as e:
                print(f"[scan] {p}: {e}")
        return count

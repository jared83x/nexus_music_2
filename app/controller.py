import random
import flet as ft
from app.config import *
from app.database import Database
from app.library import Library
from app.audio import AudioService
from app.components import track_row, card, cover_control, fmt

class AppController:
    def __init__(self,page):
        self.page=page
        self.db=Database()
        self.library=Library(self.db)
        self.audio=AudioService(page,self.position_changed,self.audio_state)
        self.tracks=[]
        self.queue=[]
        self.index=-1
        self.shuffle=False
        self.repeat=False
        self.current_playlist=None
        self.position=0
        self.duration=0

        self.body=ft.Column(expand=True,scroll=ft.ScrollMode.AUTO)
        self.search=ft.TextField(
            hint_text="¿Qué quieres reproducir?",
            prefix_icon=ft.Icons.SEARCH,
            width=360,
            border_radius=25,
            bgcolor=CARD,
            border_color="transparent",
            on_change=self.search_changed
        )

        self.now_title=ft.Text("Nada reproduciéndose",color=TEXT,weight=ft.FontWeight.BOLD)
        self.now_artist=ft.Text("",color=MUTED,size=12)
        self.now_cover=cover_control(None,54)
        self.progress=ft.Slider(min=0,max=1,value=0,expand=True,on_change=self.seek_changed)
        self.play_btn=ft.IconButton(
            ft.Icons.PLAY_CIRCLE_FILLED,icon_size=38,icon_color=TEXT,
            on_click=self.toggle
        )
        self.volume_slider=ft.Slider(min=0,max=1,value=1,width=110,on_change=self.volume_changed)
        self.shuffle_btn=ft.IconButton(ft.Icons.SHUFFLE,icon_color=MUTED,on_click=self.toggle_shuffle)
        self.repeat_btn=ft.IconButton(ft.Icons.REPEAT,icon_color=MUTED,on_click=self.toggle_repeat)

    def start(self):
        self.library.scan()
        self.tracks=list(self.db.tracks())
        self.queue=self.tracks[:]

        sidebar=self.build_sidebar()
        top=ft.Container(
            padding=18,
            content=ft.Row([
                ft.IconButton(ft.Icons.ARROW_BACK,icon_color=MUTED),
                ft.IconButton(ft.Icons.ARROW_FORWARD,icon_color=MUTED),
                self.search,
                ft.Container(expand=True),
                ft.CircleAvatar(content=ft.Icon(ft.Icons.PERSON))
            ])
        )

        player=ft.Container(
            height=94,bgcolor=SURFACE,padding=12,
            content=ft.Row([
                ft.Container(
                    width=300,
                    content=ft.Row([
                        self.now_cover,
                        ft.Column([self.now_title,self.now_artist],spacing=2,expand=True)
                    ])
                ),
                ft.Container(
                    expand=True,
                    content=ft.Column([
                        ft.Row([
                            self.shuffle_btn,
                            ft.IconButton(ft.Icons.SKIP_PREVIOUS,icon_color=TEXT,on_click=self.previous),
                            self.play_btn,
                            ft.IconButton(ft.Icons.SKIP_NEXT,icon_color=TEXT,on_click=self.next),
                            self.repeat_btn
                        ],alignment=ft.MainAxisAlignment.CENTER,height=45),
                        ft.Row([
                            ft.Text("0:00",color=MUTED,size=10),
                            self.progress,
                            ft.Text("0:00",color=MUTED,size=10)
                        ])
                    ],spacing=0)
                ),
                ft.Row([
                    ft.Icon(ft.Icons.VOLUME_UP,color=MUTED),
                    self.volume_slider
                ],width=210)
            ])
        )

        self.page.add(ft.Column(
            expand=True,spacing=0,
            controls=[
                ft.Row(
                    expand=True,spacing=0,
                    controls=[
                        sidebar,
                        ft.Container(
                            expand=True,bgcolor=BG,
                            content=ft.Column([
                                top,
                                ft.Container(expand=True,padding=25,content=self.body)
                            ])
                        )
                    ]
                ),
                player
            ]
        ))
        self.home()

    def nav_item(self,icon,label,fn):
        return ft.Container(
            content=ft.Row([ft.Icon(icon,color=MUTED),ft.Text(label,color=MUTED)]),
            padding=ft.Padding.symmetric(horizontal=10, vertical=10),
            border_radius=7,ink=True,on_click=fn,
            
        )

    def build_sidebar(self):
        return ft.Container(
            width=235,bgcolor=SIDEBAR,padding=20,
            content=ft.Column([
                ft.Text("NEXUS",size=25,weight=ft.FontWeight.BOLD,color=TEXT),
                ft.Text("MUSIC",size=11,color=GREEN,weight=ft.FontWeight.BOLD),
                ft.Container(height=20),
                #self.nav_item(ft.Icons.HOME,"Inicio",lambda e:self.home()),
                self.nav_item(ft.Icons.HOME,"Inicio", self.home()),
                #self.nav_item(ft.Icons.SEARCH,"Buscar",lambda e:self.search.focus()),
                self.nav_item(ft.Icons.SEARCH,"Buscar",self.search.focus()),
                #self.nav_item(ft.Icons.LIBRARY_MUSIC,"Biblioteca",lambda e:self.library_view()),
                self.nav_item(ft.Icons.LIBRARY_MUSIC,"Biblioteca",self.library_view()),
                ft.Container(height=20),
                ft.Text("TU BIBLIOTECA",size=11,color=MUTED),
                #self.nav_item(ft.Icons.FAVORITE,"Favoritos",lambda e:self.favorites()),
                self.nav_item(ft.Icons.FAVORITE,"Favoritos",self.favorites()),
                #self.nav_item(ft.Icons.QUEUE_MUSIC,"Playlists",lambda e:self.playlists()),
                self.nav_item(ft.Icons.QUEUE_MUSIC,"Playlists",self.playlists()),
                ft.Container(expand=True),
                ft.Text("Nexus Music 2.0",size=11,color=MUTED)
            ])
        )

    def render(self,controls):
        self.body.controls=controls
        self.page.update()

    def home(self):
        self.tracks=list(self.db.tracks())
        recent=list(self.db.recent())
        controls=[
            ft.Text("Buenos días",size=30,weight=ft.FontWeight.BOLD,color=TEXT),
            ft.Text("Tu música, tus playlists y tus favoritos.",color=MUTED)
        ]
        if recent:
            controls += [
                ft.Text("Reproducido recientemente",size=21,weight=ft.FontWeight.BOLD,color=TEXT),
                ft.Row([card(t,self.play) for t in recent],scroll=ft.ScrollMode.AUTO)
            ]
        controls += [
            ft.Text("Tu música",size=21,weight=ft.FontWeight.BOLD,color=TEXT),
            ft.Column([track_row(t,self.play,self.favorite,self.menu) for t in self.tracks])
        ]
        self.render(controls)

    def library_view(self):
        self.tracks=list(self.db.tracks())
        self.render([
            ft.Text("Tu biblioteca",size=30,weight=ft.FontWeight.BOLD,color=TEXT),
            ft.Text(f"{len(self.tracks)} canciones",color=MUTED),
            ft.Column([track_row(t,self.play,self.favorite,self.menu) for t in self.tracks])
        ])

    def favorites(self):
        tracks=list(self.db.favorites())
        self.render([
            ft.Text("Canciones que te gustan",size=30,weight=ft.FontWeight.BOLD,color=TEXT),
            ft.Text(f"{len(tracks)} canciones",color=MUTED),
            ft.Column([track_row(t,self.play,self.favorite,self.menu) for t in tracks])
        ])

    def playlists(self):
        playlists=self.db.playlists()
        name=ft.TextField(hint_text="Nombre de playlist",width=280)
        def create(e):
            if name.value.strip():
                self.db.create_playlist(name.value)
                self.playlists()
        rows=[]
        for p in playlists:
            rows.append(
                ft.Container(
                    padding=12,bgcolor=CARD,border_radius=8,
                    content=ft.Row([
                        ft.Icon(ft.Icons.QUEUE_MUSIC,color=GREEN,size=35),
                        ft.Text(p["name"],color=TEXT,expand=True,size=16),
                        ft.IconButton(ft.Icons.OPEN_IN_NEW,color=MUTED,
                                      on_click=lambda e,pid=p["id"]:self.open_playlist(pid)),
                        ft.IconButton(ft.Icons.DELETE_OUTLINE,color=MUTED,
                                      on_click=lambda e,pid=p["id"]:self.delete_playlist(pid))
                    ])
                )
            )
        self.render([
            ft.Text("Playlists",size=30,weight=ft.FontWeight.BOLD,color=TEXT),
            ft.Row([name,ft.Button("Crear playlist",on_click=create)]),
            ft.Column(rows,spacing=8)
        ])

    def open_playlist(self,playlist_id):
        p=self.db.playlist(playlist_id)
        tracks=list(self.db.playlist_tracks(playlist_id))
        self.current_playlist=playlist_id
        self.queue=tracks
        self.index=-1
        self.render([
            ft.Row([
                ft.IconButton(ft.Icons.ARROW_BACK,on_click=lambda e:self.playlists()),
                ft.Column([
                    ft.Text(p["name"],size=30,weight=ft.FontWeight.BOLD,color=TEXT),
                    ft.Text(f"{len(tracks)} canciones",color=MUTED)
                ])
            ]),
            ft.Column([
                track_row(t,self.play,self.favorite,
                          lambda t,pid=playlist_id:self.menu(t,pid))
                for t in tracks
            ])
        ])

    def delete_playlist(self,playlist_id):
        self.db.delete_playlist(playlist_id)
        self.playlists()

    def menu(self,track,playlist_id=None):
        playlists=self.db.playlists()
        actions=[]
        for p in playlists:
            actions.append(
                ft.ListTile(
                    leading=ft.Icon(ft.Icons.ADD),
                    title=ft.Text(f'Añadir a "{p["name"]}"'),
                    on_click=lambda e,pid=p["id"]:self.add_to_playlist(pid,track["id"])
                )
            )
        dlg=ft.AlertDialog(
            title=ft.Text(track["title"]),
            content=ft.Column(actions,scroll=ft.ScrollMode.AUTO) if actions else ft.Text("Crea una playlist primero."),
            actions=[ft.TextButton("Cerrar",on_click=lambda e:self.close_dialog())]
        )
        self.page.dialog=dlg
        dlg.open=True
        self.page.update()

    def add_to_playlist(self,pid,tid):
        self.db.add_to_playlist(pid,tid)
        self.close_dialog()

    def close_dialog(self):
        if self.page.dialog:
            self.page.dialog.open=False
            self.page.update()

    def search_changed(self,e):
        q=e.control.value.strip()
        tracks=list(self.db.tracks(q))
        self.render([
            ft.Text("Resultados",size=30,weight=ft.FontWeight.BOLD,color=TEXT),
            ft.Text(f"{len(tracks)} resultados",color=MUTED),
            ft.Column([track_row(t,self.play,self.favorite,self.menu) for t in tracks])
        ])

    def play(self,track):
        if self.current_playlist is None:
            self.queue=list(self.tracks)
        async def runner():
            await self.audio.play(track)
            self.db.add_history(track["id"])
            self.index=next((i for i,x in enumerate(self.queue) if x["id"]==track["id"]),0)
            self.now_title.value=track["title"]
            self.now_artist.value=track["artist"]
            self.now_cover=cover_control(track,54)
            self.play_btn.icon=ft.Icons.PAUSE_CIRCLE_FILLED
            self.progress.value=0
            self.page.update()
        self.page.run_task(runner)

    def toggle(self,e):
        async def runner():
            await self.audio.toggle()
            self.play_btn.icon=ft.Icons.PAUSE_CIRCLE_FILLED if self.audio.playing else ft.Icons.PLAY_CIRCLE_FILLED
            self.page.update()
        self.page.run_task(runner)

    def next(self,e=None):
        if not self.queue:return
        if self.shuffle:
            self.index=random.randrange(len(self.queue))
        else:
            self.index+=1
            if self.index>=len(self.queue):
                if self.repeat:self.index=0
                else:self.index=len(self.queue)-1
        self.play(self.queue[self.index])

    def previous(self,e=None):
        if not self.queue:return
        self.index-=1
        if self.index<0:self.index=len(self.queue)-1
        self.play(self.queue[self.index])

    def toggle_shuffle(self,e=None):
        self.shuffle=not self.shuffle
        self.shuffle_btn.icon_color=GREEN if self.shuffle else MUTED
        self.page.update()

    def toggle_repeat(self,e=None):
        self.repeat=not self.repeat
        self.repeat_btn.icon_color=GREEN if self.repeat else MUTED
        self.page.update()

    def favorite(self,track):
        self.db.toggle_favorite(track["id"])
        self.tracks=list(self.db.tracks())
        self.page.update()

    def volume_changed(self,e):
        self.audio.set_volume(e.control.value)

    def seek_changed(self,e):
        if not self.audio.current:return
        async def runner():
            await self.audio.seek(float(e.control.value)*self.duration*1000)
        self.page.run_task(runner)

    def position_changed(self,e):
        try:
            pos=getattr(e,"position",None)
            dur=getattr(e,"duration",None)
            if pos is None:return
            if dur:
                self.duration=float(dur)
            self.position=float(pos)
            if self.duration>0:
                self.progress.value=min(1,self.position/self.duration)
                self.progress.update()
        except Exception:
            pass

    def audio_state(self,e):
        try:
            state=str(getattr(e,"state","")).lower()
            if "completed" in state or "ended" in state:
                self.next()
        except Exception:
            pass

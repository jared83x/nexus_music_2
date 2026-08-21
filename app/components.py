import flet as ft
from app.config import *

def fmt(seconds):
    seconds=int(seconds or 0)
    return f"{seconds//60}:{seconds%60:02d}"

def cover_control(track, size=54):
    if track and track["cover"]:
        return ft.Image(src=track["cover"], width=size, height=size, fit=ft.ImageFit.COVER)
    return ft.Container(
        width=size,height=size,bgcolor=CARD_HOVER,border_radius=6,
        alignment=ft.Alignment.CENTER,
        content=ft.Icon(ft.Icons.MUSIC_NOTE,color=MUTED)
    )

def track_row(track, on_play, on_favorite, on_menu=None):
    return ft.Container(
        #padding=ft.padding.symmetric(horizontal=10,vertical=6),
        padding=ft.Padding.symmetric(horizontal=10, vertical=6),
        border_radius=8,
        ink=True,
        on_click=lambda e:on_play(track),
        #on_click=on_play(track),
        content=ft.Row([
            cover_control(track,50),
            ft.Column([
                ft.Text(track["title"],color=TEXT,weight=ft.FontWeight.BOLD,
                        max_lines=1,overflow=ft.TextOverflow.ELLIPSIS),
                ft.Text(f'{track["artist"]} • {track["album"]}',color=MUTED,size=12,
                        max_lines=1,overflow=ft.TextOverflow.ELLIPSIS)
            ],expand=True,spacing=2),
            ft.Text(fmt(track["duration"]),color=MUTED,size=12),
            ft.IconButton(
                icon=ft.Icons.FAVORITE if track["favorite"] else ft.Icons.FAVORITE_BORDER,
                icon_color=GREEN if track["favorite"] else MUTED,
                on_click=lambda e:on_favorite(track)
            ),
            ft.IconButton(
                icon=ft.Icons.MORE_VERT,
                icon_color=MUTED,
                on_click=lambda e:on_menu(track) if on_menu else None
            )
        ])
    )

def card(track,on_play):
    return ft.Container(
        width=180,padding=12,bgcolor=CARD,border_radius=10,ink=True,
        on_click=lambda e:on_play(track),
        content=ft.Column([
            ft.Container(
                width=156,height=156,border_radius=8,
                clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
                alignment=ft.Alignment.CENTER,
                content=cover_control(track,156)
            ),
            ft.Text(track["title"],color=TEXT,weight=ft.FontWeight.BOLD,
                    max_lines=1,overflow=ft.TextOverflow.ELLIPSIS),
            ft.Text(track["artist"],color=MUTED,size=12,
                    max_lines=1,overflow=ft.TextOverflow.ELLIPSIS)
        ],spacing=8)
    )

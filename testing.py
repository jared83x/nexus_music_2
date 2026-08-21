import os
import flet as ft
import flet_audio as fta


def main(page: ft.Page):
    page.title = "🎵 Flet Music Player"
    page.bgcolor = "#0f1117"
    page.padding = 0
    page.window.width = 900
    page.window.height = 700

    # ---------------------------------------------------------
    # Estado
    # ---------------------------------------------------------

    playlist = []
    current_index = -1
    current_audio = None
    is_playing = False
    duration_ms = 0
    position_ms = 0
    volume = 1.0

    # ---------------------------------------------------------
    # Elementos de interfaz
    # ---------------------------------------------------------

    song_title = ft.Text(
        "Ninguna canción seleccionada",
        size=22,
        weight=ft.FontWeight.BOLD,
        color=ft.Colors.WHITE,
        text_align=ft.TextAlign.CENTER,
    )

    song_subtitle = ft.Text(
        "Selecciona una o varias canciones",
        size=13,
        color=ft.Colors.GREY_400,
        text_align=ft.TextAlign.CENTER,
    )

    current_time = ft.Text(
        "00:00",
        size=12,
        color=ft.Colors.GREY_400,
    )

    total_time = ft.Text(
        "00:00",
        size=12,
        color=ft.Colors.GREY_400,
    )

    progress = ft.Slider(
        min=0,
        max=1,
        value=0,
        expand=True,
        active_color=ft.Colors.PURPLE_ACCENT,
        inactive_color=ft.Colors.GREY_800,
        on_change=lambda e: seek_audio(e),
    )

    volume_slider = ft.Slider(
        min=0,
        max=1,
        value=1,
        width=130,
        active_color=ft.Colors.PURPLE_ACCENT,
        inactive_color=ft.Colors.GREY_800,
        on_change=lambda e: change_volume(e),
    )

    play_button = ft.IconButton(
        icon=ft.Icons.PLAY_ARROW_ROUNDED,
        icon_size=42,
        icon_color=ft.Colors.WHITE,
        bgcolor=ft.Colors.PURPLE_ACCENT,
        tooltip="Reproducir",
        on_click=lambda e: toggle_play(),
    )

    playlist_view = ft.ListView(
        expand=True,
        spacing=5,
        padding=10,
        auto_scroll=False,
    )

    # ---------------------------------------------------------
    # Utilidades
    # ---------------------------------------------------------

    def format_time(milliseconds):
        seconds = int(milliseconds / 1000)

        minutes = seconds // 60
        seconds = seconds % 60

        return f"{minutes:02d}:{seconds:02d}"

    def update_ui():
        page.update()

    # ---------------------------------------------------------
    # Eventos del reproductor
    # ---------------------------------------------------------

    def on_position_change(e):
        nonlocal position_ms

        position_ms = e.position

        if duration_ms > 0:
            progress.value = min(position_ms / duration_ms, 1)

        current_time.value = format_time(position_ms)

        page.update()

    def on_duration_change(e):
        nonlocal duration_ms

        duration_ms = e.duration

        total_time.value = format_time(duration_ms)

        progress.value = 0

        page.update()

    def on_state_change(e):
        nonlocal is_playing

        state = str(e.state).lower()

        if "playing" in state:
            is_playing = True
            play_button.icon = ft.Icons.PAUSE_ROUNDED

        elif "paused" in state:
            is_playing = False
            play_button.icon = ft.Icons.PLAY_ARROW_ROUNDED

        elif "stopped" in state:
            is_playing = False
            play_button.icon = ft.Icons.PLAY_ARROW_ROUNDED

        page.update()

    # ---------------------------------------------------------
    # Crear reproductor
    # ---------------------------------------------------------

    def create_audio(path):
        return fta.Audio(
            src=path,
            autoplay=False,
            volume=volume,
            release_mode=fta.ReleaseMode.STOP,
            on_position_change=on_position_change,
            on_duration_change=on_duration_change,
            on_state_change=on_state_change,
        )

    # ---------------------------------------------------------
    # Reproducir canción
    # ---------------------------------------------------------

    async def play_song(index):
        nonlocal current_index
        nonlocal current_audio
        nonlocal is_playing
        nonlocal duration_ms
        nonlocal position_ms

        if not playlist:
            return

        if index < 0 or index >= len(playlist):
            return

        # Detener y liberar el reproductor anterior
        if current_audio is not None:
            try:
                await current_audio.release()
            except Exception:
                pass

            try:
                page.services.remove(current_audio)
            except ValueError:
                pass

        current_index = index
        duration_ms = 0
        position_ms = 0

        song = playlist[index]

        song_title.value = song["name"]
        song_subtitle.value = song["path"]

        current_time.value = "00:00"
        total_time.value = "00:00"
        progress.value = 0

        current_audio = create_audio(song["path"])

        page.services.append(current_audio)

        await current_audio.play()

        is_playing = True
        play_button.icon = ft.Icons.PAUSE_ROUNDED

        update_playlist_ui()

        page.update()

    # ---------------------------------------------------------
    # Play / Pause
    # ---------------------------------------------------------

    async def toggle_play():
        nonlocal is_playing

        if current_audio is None:
            if playlist:
                await play_song(0)

            return

        if is_playing:
            await current_audio.pause()

            is_playing = False
            play_button.icon = ft.Icons.PLAY_ARROW_ROUNDED

        else:
            await current_audio.resume()

            is_playing = True
            play_button.icon = ft.Icons.PAUSE_ROUNDED

        page.update()

    # ---------------------------------------------------------
    # Canción anterior
    # ---------------------------------------------------------

    async def previous_song():
        if not playlist:
            return

        if current_index <= 0:
            await play_song(len(playlist) - 1)
        else:
            await play_song(current_index - 1)

    # ---------------------------------------------------------
    # Canción siguiente
    # ---------------------------------------------------------

    async def next_song():
        if not playlist:
            return

        if current_index >= len(playlist) - 1:
            await play_song(0)
        else:
            await play_song(current_index + 1)

    # ---------------------------------------------------------
    # Seek
    # ---------------------------------------------------------

    async def seek_audio(e):
        if current_audio is None:
            return

        if duration_ms <= 0:
            return

        new_position = int(e.control.value * duration_ms)

        await current_audio.seek(
            ft.Duration(milliseconds=new_position)
        )

    # ---------------------------------------------------------
    # Volumen
    # ---------------------------------------------------------

    def change_volume(e):
        nonlocal volume

        volume = e.control.value

        if current_audio is not None:
            current_audio.volume = volume

        page.update()

    # ---------------------------------------------------------
    # File Picker
    # ---------------------------------------------------------

    file_picker = ft.FilePicker()

    page.services.append(file_picker)

    async def pick_music(e):
        files = await file_picker.pick_files(
            allow_multiple=True,
            file_type=ft.FilePickerFileType.CUSTOM,
            allowed_extensions=[
                "mp3",
                "wav",
                "ogg",
                "flac",
                "m4a",
                "aac",
            ],
        )

        if not files:
            return

        for file in files:
            if not file.path:
                continue

            # Evitar duplicados
            already_exists = any(
                song["path"] == file.path
                for song in playlist
            )

            if already_exists:
                continue

            playlist.append(
                {
                    "name": file.name,
                    "path": file.path,
                }
            )

        update_playlist_ui()

        # Si todavía no hay canción, reproducir la primera
        if current_audio is None and playlist:
            await play_song(0)

    # ---------------------------------------------------------
    # Lista de reproducción
    # ---------------------------------------------------------

    def update_playlist_ui():
        playlist_view.controls.clear()

        for index, song in enumerate(playlist):

            selected = index == current_index

            icon = (
                ft.Icons.MUSIC_NOTE
                if not selected
                else ft.Icons.GRAPHIC_EQ
            )

            text_color = (
                ft.Colors.PURPLE_ACCENT
                if selected
                else ft.Colors.WHITE
            )

            item = ft.Container(
                content=ft.Row(
                    controls=[
                        ft.Icon(
                            icon,
                            color=text_color,
                            size=22,
                        ),

                        ft.Column(
                            controls=[
                                ft.Text(
                                    song["name"],
                                    color=text_color,
                                    size=14,
                                    weight=(
                                        ft.FontWeight.BOLD
                                        if selected
                                        else ft.FontWeight.NORMAL
                                    ),
                                    max_lines=1,
                                    overflow=ft.TextOverflow.ELLIPSIS,
                                ),

                                ft.Text(
                                    os.path.dirname(song["path"]),
                                    color=ft.Colors.GREY_500,
                                    size=11,
                                    max_lines=1,
                                    overflow=ft.TextOverflow.ELLIPSIS,
                                ),
                            ],
                            spacing=2,
                            expand=True,
                        ),
                    ],
                    spacing=12,
                ),
                padding=12,
                border_radius=10,
                bgcolor=(
                    "#242036"
                    if selected
                    else "#171a22"
                ),
                ink=True,
                on_click=lambda e, i=index: play_song(i),
            )

            playlist_view.controls.append(item)

        page.update()

    # ---------------------------------------------------------
    # Limpiar playlist
    # ---------------------------------------------------------

    async def clear_playlist(e):
        nonlocal current_audio
        nonlocal current_index
        nonlocal is_playing

        if current_audio is not None:
            try:
                await current_audio.release()
            except Exception:
                pass

            try:
                page.services.remove(current_audio)
            except ValueError:
                pass

        current_audio = None
        current_index = -1
        is_playing = False

        playlist.clear()

        song_title.value = "Ninguna canción seleccionada"
        song_subtitle.value = "Selecciona una o varias canciones"

        current_time.value = "00:00"
        total_time.value = "00:00"
        progress.value = 0

        play_button.icon = ft.Icons.PLAY_ARROW_ROUNDED

        update_playlist_ui()

    # ---------------------------------------------------------
    # INTERFAZ
    # ---------------------------------------------------------

    header = ft.Container(
        content=ft.Row(
            controls=[
                ft.Icon(
                    ft.Icons.MUSIC_NOTE_ROUNDED,
                    color=ft.Colors.PURPLE_ACCENT,
                    size=32,
                ),

                ft.Text(
                    "Flet Music",
                    size=25,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.WHITE,
                ),

                ft.Container(expand=True),

                ft.Button(
                    content="Agregar música",
                    icon=ft.Icons.ADD,
                    on_click=pick_music,
                    style=ft.ButtonStyle(
                        bgcolor=ft.Colors.PURPLE_ACCENT,
                        color=ft.Colors.WHITE,
                    ),
                ),
            ],
        ),
        padding=20,
    )

    album_art = ft.Container(
        content=ft.Icon(
            ft.Icons.ALBUM_ROUNDED,
            size=100,
            color=ft.Colors.WHITE,
        ),
        width=220,
        height=220,
        border_radius=20,
        bgcolor="#29223d",
        alignment=ft.Alignment.CENTER,
    )

    player_controls = ft.Column(
        controls=[
            song_title,
            song_subtitle,

            ft.Row(
                controls=[
                    current_time,
                    progress,
                    total_time,
                ],
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),

            ft.Row(
                controls=[
                    ft.IconButton(
                        icon=ft.Icons.SKIP_PREVIOUS_ROUNDED,
                        icon_size=32,
                        icon_color=ft.Colors.WHITE,
                        tooltip="Anterior",
                        on_click=lambda e: previous_song(),
                    ),

                    play_button,

                    ft.IconButton(
                        icon=ft.Icons.SKIP_NEXT_ROUNDED,
                        icon_size=32,
                        icon_color=ft.Colors.WHITE,
                        tooltip="Siguiente",
                        on_click=lambda e: next_song(),
                    ),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
            ),

            ft.Row(
                controls=[
                    ft.Icon(
                        ft.Icons.VOLUME_DOWN_ROUNDED,
                        color=ft.Colors.GREY_400,
                    ),

                    volume_slider,

                    ft.Icon(
                        ft.Icons.VOLUME_UP_ROUNDED,
                        color=ft.Colors.GREY_400,
                    ),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
        ],
        spacing=12,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    )

    player_panel = ft.Container(
        content=ft.Column(
            controls=[
                album_art,
                player_controls,
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=20,
        ),
        padding=30,
        expand=1,
    )

    playlist_header = ft.Row(
        controls=[
            ft.Text(
                "Playlist",
                size=20,
                weight=ft.FontWeight.BOLD,
                color=ft.Colors.WHITE,
            ),

            ft.Container(expand=True),

            ft.IconButton(
                icon=ft.Icons.DELETE_OUTLINE_ROUNDED,
                icon_color=ft.Colors.GREY_400,
                tooltip="Limpiar playlist",
                on_click=clear_playlist,
            ),
        ],
    )

    playlist_panel = ft.Container(
        content=ft.Column(
            controls=[
                playlist_header,
                playlist_view,
            ],
            expand=True,
        ),
        width=380,
        padding=20,
        bgcolor="#12151d",
        border_radius=15,
    )

    # ---------------------------------------------------------
    # Layout principal
    # ---------------------------------------------------------

    page.add(
        ft.Column(
            controls=[
                header,

                ft.Container(
                    content=ft.Row(
                        controls=[
                            player_panel,
                            playlist_panel,
                        ],
                        expand=True,
                        spacing=15,
                    ),
                    expand=True,
                    padding=ft.Padding(
                        left=20,
                        right=20,
                        bottom=20,
                        top=0,
                    ),
                ),
            ],
            expand=True,
        )
    )


if __name__ == "__main__":
    ft.run(main)

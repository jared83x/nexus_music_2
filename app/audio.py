import flet as ft
import flet_audio as fta

class AudioService:
    def __init__(self, page, on_position=None, on_state=None):
        self.page=page
        self.on_position=on_position
        self.on_state=on_state
        self.audio=fta.Audio(autoplay=False, volume=1.0)
        #self.page.overlay.append(self.audio)
        self.page.services.append(self.audio)
        self.current=None
        self.playing=False

        try:
            self.audio.on_position_changed=self._position
            self.audio.on_state_changed=self._state
        except Exception:
            pass

    def _position(self,e):
        if self.on_position:
            self.on_position(e)

    def _state(self,e):
        if self.on_state:
            self.on_state(e)

    async def play(self, track):
        await self.audio.release()
        self.audio.src=track["path"]
        await self.audio.play()
        self.current=track
        self.playing=True

    async def pause(self):
        await self.audio.pause()
        self.playing=False

    async def resume(self):
        await self.audio.resume()
        self.playing=True

    async def toggle(self):
        if not self.current:
            return
        if self.playing:
            await self.pause()
        else:
            await self.resume()

    async def seek(self, milliseconds):
        await self.audio.seek(int(milliseconds))

    def set_volume(self, value):
        self.audio.volume=max(0,min(1,float(value)))

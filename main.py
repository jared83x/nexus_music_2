import flet as ft
from app.controller import AppController

def main(page: ft.Page):
    AppController(page).start()

if __name__ == "__main__":
    ft.run(main)

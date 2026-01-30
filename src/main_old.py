from flet import Text, TextField, FloatingActionButton, Checkbox
# Layout
from flet import Column, Row
from flet import DatePickerEntryMode, KeyboardType, ScrollMode

import flet as ft
# Colors
from flet import Colors

from TodoApp import TodoApp
from SelectRoom import SelectRoom
from Recherche import Recherche
    
class Reservation(Column):
    def __init__(self, page, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.page = page
        
        self.recherche = Recherche(up_parent=self, page=page)
        self.selectRoom = SelectRoom(up_parent=self, page=page, visible=False)
        
        self.controls = [
            self.recherche,
            self.selectRoom
        ]
    
    async def show_room(self, checkIn_dt, checkOut_dt):
        await self.selectRoom.fetch_data_async(checkIn_dt, checkOut_dt)
        

async def main(page: ft.Page):
    page.title = "Test Application"

    page.theme_mode = ft.ThemeMode.LIGHT
    
    page.window.width = 800
    page.window.height = 800
    page.window.center()
    page.scroll = ScrollMode.AUTO
    
    page.locale_configuration = ft.LocaleConfiguration(
        supported_locales=[
            ft.Locale("de", "DE"),  # German, Germany
            ft.Locale("fr", "FR"),  # French, France
            ft.Locale("es"),        # Spanish
        ],
        current_locale=ft.Locale("fr", "FR"),
    )
    
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    
    # todo = TodoApp()
    
    reservation = Reservation(page=page)
    
    page.add(reservation)

if __name__ == "__main__":
    ft.app(main)

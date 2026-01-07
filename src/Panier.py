from __future__ import annotations

from flet import Text, TextField, FloatingActionButton, Checkbox, Button, FilledButton, Icons, Icon
# Layout
from flet import Column, Row, Tabs, Tab, ExpansionTile, Container
from flet import DatePickerEntryMode, KeyboardType
from flet import Colors

import datetime as dt

import flet as ft
# Colors
from flet import Colors
from functools import partial
from loguru import logger

from typing import TYPE_CHECKING

# Ce bloc ne s'exécute JAMAIS quand le script tourne.
# Il est lu uniquement par votre IDE (VSCode, PyCharm) ou Mypy.
if TYPE_CHECKING:
    from SelectRoom import SelectRoom




class Panier(Column):
    def __init__(self, up_parent: SelectRoom, panier_button, data:list = [], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.up_parent = up_parent
        # list : (room_id, (checkIn, checkOut))
        self.data : list[
            tuple[
                str, tuple[dt.date, dt.date]
            ]] = data
        self.panier_button = panier_button
        
        # if not data:
        #     self.controls = [Text("vide")]
            
        self.reserver_button = FilledButton(text="Réserver", disabled=True)
        
        if not data:
            self.controls = [Text("vide")]
        self.panier_room = Column(controls=[Text("vide")])
        
        # self.controls.append(self.reserver_button)
        self.controls = [
            self.panier_room,
            self.reserver_button
        ]
        
        
    def add_room(self, room:str):
        self.data.append((room, self.up_parent.dates))
        
        # logger.debug(self.data)
        
        # self.controls = [ft.ListTile(title=ft.Text(book[0], book[1])) for book in self.data]
        # if self.data:
        #     self.reserver_button.disabled = False
        # self.controls.append(self.reserver_button)
        # self.update()
        self._update_panier()

    def _update_panier(self):
        self.panier_button.badge = str(len(self.data))
        self.panier_button.update()

        if not self.data:
            self.panier_room.controls = [Text("vide")]
            self.reserver_button.disabled = True
        else:
            self.panier_room.controls = [ft.ListTile(title=ft.Text(f"{book[0]}, {book[1]}")) for book in self.data]
            self.reserver_button.disabled = False
        self.update()
from __future__ import annotations

from flet import Text, TextField, FloatingActionButton, Checkbox, Button, FilledButton, Icons, Icon
# Layout
from flet import Column, Row, Tabs, Tab, ExpansionTile, Container, ResponsiveRow
from flet import DatePickerEntryMode, KeyboardType
from flet import Colors

import datetime as dt

import flet as ft
# Colors
from flet import Colors
from functools import partial
from loguru import logger
import os, yaml


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
HOSTS_YAML = os.path.join(BASE_DIR, 'config.yml')
with open(HOSTS_YAML, "r") as f_in:
    HOSTS = yaml.safe_load(f_in)["hosts"]  # [{number: 1, name: single}, {number: 2, name: double}, etc..]


class ListRoom(Column):
    def __init__(self, up_parent, data : dict, panier, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        logger.debug(f"ListRoom init id: {hex(id(self))}")
        self.up_parent = up_parent
        logger.debug(f"ListRoom up_parent init id: {hex(id(self.up_parent))}")
        self.data : dict = data
        
        self.panier = panier
        
        self.show_personnes(update=False)
        
        
    def show_personnes(self, e=None, update=True):
        self.controls = []
        for host in HOSTS:
            self.controls.append(
                GuestCard(number=host["number"], name=host["name"], on_click = lambda e, host=host["number"]: self.filter_rooms_by_guests(host))
            )
            self.controls.append(ft.Divider())
        if update:
            self.update()
    
    def filter_rooms_by_guests(self, number:int):
        self.controls = [
            FilledButton("RETOUR", on_click=self.show_personnes),
            ft.Divider()
        ]
        resultat = dict(sorted(
            self.data.items(),
            key= lambda item: (-(item[1]["avail"] > 0), -item[1]["price"])
        ))
        # for room_id, room_data in self.data.items():
        for room_id, room_data in resultat.items():
            if room_data["occupancy"] == number:
                self.controls.append(
                    RoomCard(
                        up_parent = self,
                        name = room_data["name"],
                        price = room_data["price"],
                        avail = room_data["avail"],
                        occupancy = room_data["occupancy"],
                        on_click = lambda e, room_id=room_id: self.add_panier(room_id)
                    )
                )
                self.controls.append(ft.Divider())
        self.update()
        
    def add_panier(self, room_id, e=None):
        self.panier.add_room(room_id)
        self.show_personnes()
        self.up_parent.page.scroll_to(key="panier", duration=1000)
        
class RoomCard(Container):
    def __init__(self, up_parent, name, price, avail, occupancy, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.up_parent = up_parent
        
        self.name = name
        self.price = price
        self.avail = avail
        self.occupancy = occupancy
        
        if avail == 0:
            self.bgcolor = Colors.RED_200
        
        taxeSejour = occupancy * 2
        petitDejTaxeSejour = occupancy * 12
        
        self.content = Column([
            Row([
                Icon(Icons.ADD),
                Text(name),
                Text(f"Dispo: {avail}")]),
            Text(f"Prix (taxe séjour inclus): {price + taxeSejour}", bgcolor=Colors.YELLOW_700),
            Text(f"Prix (Petit-Dej et taxe séjour inclus): {price + petitDejTaxeSejour}", bgcolor=Colors.GREEN_500),
        ])

        
        
class GuestCard(Container):
    def __init__(self, number, name, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.content = Row([Icon(Icons.MAN)] * number + [Text(name)])
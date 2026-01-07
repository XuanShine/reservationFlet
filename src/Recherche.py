from flet import Text, TextField, FloatingActionButton, Checkbox, Button, FilledButton, Icon, Icons
# Layout
from flet import Column, Row, Tabs, Tab
from flet import DatePickerEntryMode, KeyboardType, ScrollMode
from flet import Colors

import datetime as dt

import asyncio
import httpx

import flet as ft
# Colors
from flet import Colors

import json

from loguru import logger


class Recherche(Column):
    def __init__(self, up_parent, page: ft.Page, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.up_parent = up_parent
        self.page : ft.Page= page
        
        self.checkIn_dt = dt.date.today()
        self.checkIn_field = TextField(
            label="Arrivé",
            value=str(self.checkIn_dt), 
            icon=ft.Icons.CALENDAR_MONTH,
            on_click=lambda e: page.open(
                ft.DatePicker(
                    first_date=dt.date.today() - dt.timedelta(days=1),
                    current_date = self.checkIn_dt,
                    date_picker_entry_mode=DatePickerEntryMode.CALENDAR_ONLY,
                    help_text="Arrivé - Check-In",
                    on_change=self.handle_check_in_change,
                    on_dismiss=self.handle_check_in_change
                )
            )
        )
        
        self.checkOut_dt = dt.date.today() + dt.timedelta(days=1)
        self.checkOut_field = TextField(
            label="Départ",
            value=str(self.checkOut_dt), 
            icon=ft.Icons.CALENDAR_MONTH,
            on_click=self.open_calendar_check_out
        )

        self.delta = Text(str((self.checkOut_dt - self.checkIn_dt).days))

        self.controls = [
            Text(value="Réserver", expand=True),
            self.checkIn_field,
            self.checkOut_field,
            Row([
                Text("Nombre jours:"),
                self.delta
            ]),
            FilledButton(text="Rechercher", on_click=self.rechercher)
        ]
    
    def open_calendar_check_out(self, e=None):
        self.page.open(
            ft.DatePicker(
                first_date=dt.date.today() - dt.timedelta(days=1),
                current_date = self.checkOut_dt,
                date_picker_entry_mode=DatePickerEntryMode.CALENDAR_ONLY,
                help_text="Depart - Check-Out",
                on_change=self.handle_check_out_change,
                on_dismiss=self.handle_check_out_change
            )
        )
        
        
    def handle_check_in_change(self, e: ft.ControlEvent):
        newDate = e.control.value.date()
        self.checkIn_dt = self.checkIn_field.value = newDate
        if newDate >= self.checkOut_dt:
            self.checkOut_dt = self.checkOut_field.value = newDate + dt.timedelta(days=1)
        self.delta.value = (self.checkOut_dt - self.checkIn_dt).days
        self.update()
        self.open_calendar_check_out()
    
    async def handle_check_out_change(self, e: ft.ControlEvent):
        newDate = e.control.value.date()
        if newDate <= self.checkIn_dt:
            self.checkIn_dt = self.checkIn_field.value = newDate
            self.checkOut_dt = self.checkOut_field.value = newDate + dt.timedelta(days=1)
        else:
            self.checkOut_dt = self.checkOut_field.value = newDate
        self.delta.value = (self.checkOut_dt - self.checkIn_dt).days
        self.update()
        await self.rechercher()
        
    async def rechercher(self, e: ft.ControlEvent | None = None):
        await self.up_parent.show_room(self.checkIn_dt, self.checkOut_dt) # type: ignore
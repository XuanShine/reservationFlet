import asyncio
import datetime as dt
import os
import sys
from pathlib import Path
from unittest import result
from datetime import datetime

import flet as ft
import httpx
from dotenv import load_dotenv
from fastapi import Depends
from fastapi.concurrency import run_in_threadpool
from loguru import logger

from .views.menu import appbar

load_dotenv()

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


class Reservation(ft.View):
    def __init__(self, route: str = "/reservation", *args, **kwargs):
        super().__init__(route=route, *args, **kwargs)
        self.appbar = appbar
        self.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        self.scroll = ft.ScrollMode.AUTO
        
        self.controls = [
            ft.Text("Page de Réservation - En construction", size=24, weight=ft.FontWeight.BOLD),
        ]
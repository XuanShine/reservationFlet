import asyncio
import datetime as dt
import os
import sys
from pathlib import Path
from unittest import result

import flet as ft
import httpx
from dotenv import load_dotenv
from fastapi import Depends
from fastapi.concurrency import run_in_threadpool
from loguru import logger

from .views.menu import appbar


# from utils import fetch_active_client, fetch_clients

load_dotenv()


class Home_Page(ft.View):
    def __init__(self, route: str = "/", *args, **kwargs):
        super().__init__(route=route, *args, **kwargs)
        
        self.vertical_alignment = ft.MainAxisAlignment.CENTER
        self.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        # self.start_button = ft.Button("Commencer l'enregistrement", on_click=self.start_registration)
        
        self.appbar = appbar

        
        self.controls = [
            ft.Text("Page d'accueil du réceptionniste", size=24, weight=ft.FontWeight.BOLD),
        ]
    


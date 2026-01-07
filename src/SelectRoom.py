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

from ListRoom import ListRoom
from Panier import Panier
import json

from loguru import logger

class SelectRoom(Column):
    def __init__(self, up_parent, page, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.up_parent = up_parent
        self.page = page
        
        self.api_url = "http://127.0.0.1:8000/wubook/api/get_rooms_between"
        
        # --- Les éléments de l'interface ---
        self.status_text = ft.Text("Prêt à charger", color=Colors.GREY)
        self.result_container = ft.Container(
            content=ft.Text("Aucune donnée", italic=True),
            padding=10,
            bgcolor=Colors.BLUE_GREY_50,
            border_radius=5
        )
        self.loader = ft.ProgressRing(width=20, height=20, visible=False)

        # On ajoute tout ça à la colonne (self.controls)
        self.controls = [
            ft.Row([self.loader]),
            self.status_text,
            self.result_container
        ]

    # 2. La fonction Asynchrone (Le cœur du sujet)
    async def fetch_data_async(self, checkIn_dt:dt.date, checkOut_dt:dt.date):
        self.dates = (checkIn_dt, checkOut_dt)
        date_in = checkIn_dt.strftime("%d-%m-%Y")
        date_out = checkOut_dt.strftime("%d-%m-%Y")
        url = f"{self.api_url}/{date_in}/{date_out}"
        
        self.visible = True
        
        # A. UI : Mode "Chargement"
        # self.btn.disabled = True
        self.loader.visible = True
        self.status_text.visible = True
        self.status_text.value = "Veuillez patienter..."
        self.status_text.color = Colors.BLUE
        self.update() # Rafraîchit seulement ce composant

        try:
            # B. Logique : Appel HTTP Non-bloquant
            # On utilise 'async with' pour gérer la fermeture propre de la connexion
            async with httpx.AsyncClient() as client:       
                response = await client.get(url)
                response.raise_for_status() # Lève une erreur si 404/500
                
                data = response.json()

            # C. UI : Affichage du succès
            title = data.get('title', 'Sans titre')
            body = data.get('body', 'Pas de contenu')
            
            # self.panier_button = PanierButton(parent=self, data=None, on_click=self.show_panier)
            self.panier_button = FloatingActionButton(content=Icon(Icons.SHOPPING_BASKET_OUTLINED), on_click=self.show_panier)
            
            self.panier = Panier(up_parent=self, data=[], panier_button=self.panier_button, key="panier")
            # Mise à jour du contenu
            self.result_container.content = ft.Column([
                ft.Text(f"Titre : {title}", weight=ft.FontWeight.BOLD),
                ft.Divider(),
                ListRoom(up_parent=self, data=data, panier=self.panier),
                ft.Divider(),
                self.panier_button,
                ft.Divider(),
                self.panier
                # ft.Text(data),
            ])
            self.status_text.value = "Données reçues avec succès (200 OK)"
            self.status_text.color = Colors.GREEN
            self.status_text.visible = False

        except httpx.HTTPStatusError as err:
            logger.error(f"Erreur Serveur : {err.response.status_code}")
            self.status_text.value = f"Erreur Serveur\nVeuillez Réessayer"
            self.status_text.color = Colors.RED
            self.status_text.visible = True
            
        except httpx.RequestError as err:
            logger.error(f"Erreur de Connexion : {err}")
            self.status_text.value = f"Erreur de Connexion\nVeuillez Réessayer"
            self.status_text.color = Colors.RED
            self.status_text.visible = True
            
        except Exception as err:
            logger.error(f"Erreur inattendue : {err}")
            self.status_text.value = f"Erreur inattendue\nVeuillez Réessayer"
            self.status_text.color = Colors.RED
            self.status_text.visible = True

        finally:
            # D. UI : Retour à la normale (quoi qu'il arrive)
            # self.btn.disabled = False
            self.loader.visible = False
            self.visible = True
            self.update()
    
    def show_panier(self, e):
        # self.panier.visible = not self.panier.visible
        self.update()
        self.page.scroll_to(key="panier", duration=1000) # type: ignore
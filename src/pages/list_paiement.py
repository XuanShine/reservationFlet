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
from api_stancer import get_payment_intents, list_customers
try:
    from shared.schemas import PaymentIntentStancerSchema
except ImportError:
    from schemas import PaymentIntentStancerSchema

load_dotenv()

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


class List_Paiements(ft.View):
    def __init__(self, route: str = "/list", *args, **kwargs):
        super().__init__(route=route, *args, **kwargs)
        self.appbar = appbar
        self.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        self.scroll = ft.ScrollMode.AUTO
        
        self.loader = ft.ProgressRing(width=20, height=20, stroke_width=4)
        self.payments_list = []
        self.customers_cache = {}  # Cache: customer_id -> customer_name
        
        # Add payment button
        self.add_button = ft.ElevatedButton(
            "Ajouter un paiement",
            icon=ft.Icons.ADD,
            on_click=self.goto_add_paiement,
        )
        
        # Refresh button
        self.refresh_button = ft.IconButton(
            icon=ft.Icons.REFRESH,
            tooltip="Actualiser",
            on_click=lambda e: self.page.run_task(self.load_payments_async),
        )
        
        # Payment cards container
        self.payments_container = ft.Column(
            controls=[],
            spacing=10,
            scroll=ft.ScrollMode.AUTO,
        )
        
        self.controls = [
            ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Row(
                            controls=[
                                ft.Text("Liste des Paiements", size=24, weight=ft.FontWeight.BOLD),
                                ft.Row(
                                    controls=[
                                        self.loader,
                                        self.refresh_button,
                                        self.add_button,
                                    ],
                                    spacing=10,
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        ),
                        ft.Divider(),
                        self.payments_container,
                    ],
                    spacing=20,
                ),
                padding=20,
            )
        ]
    
    def did_mount(self):
        self.page.run_task(self.load_payments_async)
    
    async def goto_add_paiement(self, e):
        """Navigate to add payment page"""
        self.page.go("/add_paiement")
    
    def goto_paiement_detail(self, paiement_id):
        """Navigate to payment detail page"""
        self.page.go(f"/paiement/{paiement_id}")
    
    def create_payment_card(self, payment: PaymentIntentStancerSchema):
        """Create a payment card"""
        # logger.debug(f"Creating card for payment: {payment}")
        paiement_id = payment.id
        amount = payment.real_amount  # Uses computed field (amount/100)
        description = payment.description or ""
        created_at = payment.created_at  # Unix timestamp
        customer_id = payment.customer  # customer is a string ID, not an object
        
        # Format date from timestamp
        created_formatted = ""
        if created_at:
            try:
                from datetime import datetime as dt
                created_formatted = dt.fromtimestamp(created_at).strftime('%d/%m/%Y %H:%M')
            except Exception as e:
                logger.warning(f"Error formatting date: {e}")
                created_formatted = str(created_at)
        
        # Customer info - lookup name from cache
        customer_name = self.customers_cache.get(customer_id, "") if customer_id else ""
        
        # Status color - PaymentIntent statuses differ from Payment statuses
        if not payment.status or payment.status in ["require_payment_method", "require_authentication", "require_authorization"]:
            status_color = ft.Colors.ORANGE
            status_text = "En attente"
        elif payment.status in ["canceled", "unpaid"]:
            status_color = ft.Colors.RED
            status_text = "Échoué"
        elif payment.status in ["captured", "authorized", "processing"]:
            status_color = ft.Colors.GREEN
            status_text = "Payé"
        else:
            logger.warning(f"Unknown payment status: {payment.status}")
            status_color = ft.Colors.ORANGE
            status_text = f"Status inconnu: {payment.status}"
        
        return ft.Card(
            content=ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Row(
                            controls=[
                                ft.Column(
                                    controls=[
                                        ft.Text(customer_name or "Sans client", size=16, weight="bold"),
                                        ft.Text(description, size=14),
                                    ],
                                    spacing=5,
                                ),
                                ft.Column(
                                    controls=[
                                        ft.Container(
                                            content=ft.Text(
                                                status_text,
                                                color=ft.Colors.WHITE,
                                                size=12,
                                            ),
                                            bgcolor=status_color,
                                            padding=5,
                                            border_radius=5,
                                        ),
                                        ft.Text(f"{amount:.2f} €", size=18, weight="bold"),
                                    ],
                                    horizontal_alignment=ft.CrossAxisAlignment.END,
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        ),
                        ft.Text(f"Créé le: {created_formatted}", size=12, color=ft.Colors.GREY),
                        ft.Text(f"ID: {payment.id}", size=12, color=ft.Colors.GREY),
                        # ft.Text(f"Url: {payment.url or 'N/A'}", size=12, color=ft.Colors.GREY),
                    ],
                    spacing=10,
                ),
                padding=15,
                on_click=lambda e: self.goto_paiement_detail(paiement_id),
            ),
        )
    
    async def load_payments_async(self):
        """Load payments from API"""
        # TODO: class of ft.Card to refresh independently the status
        self.loader.visible = True
        
        # Load customers list and build cache
        try:
            customers_list = await run_in_threadpool(list_customers)
            self.customers_cache = {c.id: c.name for c in customers_list}
        except Exception as e:
            logger.warning(f"Error loading customers: {e}")
            self.customers_cache = {}
        
        self.payments_list = await run_in_threadpool(get_payment_intents)
        self.loader.visible = False
        if self.payments_list:
            self.payments_container.controls.clear()
            self.payments_container.controls.append(ft.Text(f"Mise à jour: {datetime.now().strftime('%H:%M:%S')}", size=12, color=ft.Colors.GREY))
            # Create cards for each payment
            for payment in self.payments_list:
                card = self.create_payment_card(payment)
                self.payments_container.controls.append(card)
        else:
            self.payments_container.controls.append(
                ft.Text("Aucun paiement trouvé", size=16, color=ft.Colors.GREY)
            )
        
        self.update()
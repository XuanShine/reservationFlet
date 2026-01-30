import sys
from pathlib import Path
from datetime import datetime

import flet as ft
from fastapi.concurrency import run_in_threadpool
from loguru import logger

from .views.menu import appbar
from api_stancer import get_payment_intent
try:
    from shared.schemas import PaymentIntentDetailsSchema
except ImportError:
    from schemas import PaymentIntentDetailsSchema

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


class Paiement_Detail(ft.View):
    def __init__(self, route: str, paiement_id: str, *args, **kwargs):
        super().__init__(route=route, *args, **kwargs)
        self.paiement_id = paiement_id
        self.appbar = appbar
        self.scroll = ft.ScrollMode.AUTO
        
        self.loader = ft.ProgressRing(width=16, height=16, stroke_width=2)
        self.payment_data: PaymentIntentDetailsSchema | None = None
        
        # Main content container
        self.content_container = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text("Détails du Paiement", size=24, weight=ft.FontWeight.BOLD),
                    ft.Divider(),
                    self.loader,
                ],
                spacing=20,
            ),
            padding=20,
        )
        
        self.controls = [
            self.content_container
        ]
    
    def did_mount(self):
        self.page.run_task(self.load_payment_detail_async)
    
    def get_status_info(self, status: str | None) -> tuple[ft.Colors, str]:
        """Get status color and text based on PaymentIntent status"""
        if not status or status in ["require_payment_method", "require_authentication", "require_authorization"]:
            return ft.Colors.ORANGE, "En attente"
        elif status in ["canceled", "unpaid"]:
            return ft.Colors.RED, "Échoué"
        elif status in ["captured", "authorized", "processing"]:
            return ft.Colors.GREEN, "Payé"
        else:
            logger.warning(f"Unknown payment status: {status}")
            return ft.Colors.ORANGE, f"Status: {status}"
    
    async def load_payment_detail_async(self):
        """Load payment details from Stancer API"""
        try:
            payment_data = await run_in_threadpool(get_payment_intent, self.paiement_id)
            self.payment_data = payment_data
        except Exception as e:
            logger.error(f"Error loading payment detail: {e}")
            self.payment_data = None
        
        self.loader.visible = False
        
        if self.payment_data:
            # Status badge
            status_color, status_text = self.get_status_info(self.payment_data.status)
            
            # Format date from timestamp
            created_formatted = ""
            if self.payment_data.created_at:
                try:
                    created_formatted = datetime.fromtimestamp(self.payment_data.created_at).strftime('%d/%m/%Y %H:%M')
                except Exception as e:
                    logger.warning(f"Error formatting date: {e}")
                    created_formatted = str(self.payment_data.created_at)
            
            # Customer info from customerStancer (full CustomerStancerSchema object)
            customer = self.payment_data.customerStancer
            customer_name = customer.name if customer else ""
            customer_email = customer.email if customer else ""
            customer_phone = customer.mobile if customer else ""
            
            # Amount (real_amount is computed field: amount/100)
            amount = self.payment_data.real_amount
            
            # Build detail view
            details = ft.Column(
                controls=[
                    # Status
                    ft.Row([
                        ft.Text("Statut:", weight="bold", size=16),
                        ft.Container(
                            content=ft.Text(
                                status_text,
                                color=ft.Colors.WHITE,
                                size=14,
                                weight="bold"
                            ),
                            bgcolor=status_color,
                            padding=8,
                            border_radius=8
                        ),
                    ]),
                    
                    # Customer info
                    ft.Text("Informations Client", size=18, weight=ft.FontWeight.BOLD),
                    ft.Card(
                        content=ft.Container(
                            content=ft.Column([
                                ft.Row([
                                    ft.Icon(ft.Icons.PERSON, size=20, color=ft.Colors.PRIMARY),
                                    ft.Text(customer_name or "Sans client", weight="bold", size=16, selectable=True),
                                ]),
                                ft.Row([
                                    ft.Icon(ft.Icons.EMAIL, size=16, color=ft.Colors.GREY),
                                    ft.Text(customer_email or "N/A", size=14, selectable=True),
                                    ft.ElevatedButton(
                                        "Copier",
                                        icon=ft.Icons.COPY,
                                        on_click=lambda e, email=customer_email: self.page.run_task(self.copy_to_clipboard, email),
                                    ) if customer_email else ft.Container(),
                                ]),
                                ft.Row([
                                    ft.Icon(ft.Icons.PHONE, size=16, color=ft.Colors.GREY),
                                    ft.Text(customer_phone or "N/A", size=14, selectable=True),
                                    ft.ElevatedButton(
                                        "Copier",
                                        icon=ft.Icons.COPY,
                                        on_click=lambda e, phone=customer_phone: self.page.run_task(self.copy_to_clipboard, phone),
                                    ) if customer_phone else ft.Container(),
                                ]),
                            ], spacing=8),
                            padding=15,
                        )
                    ),
                    
                    # Payment info
                    ft.Text("Informations Paiement", size=18, weight=ft.FontWeight.BOLD),
                    ft.Card(
                        content=ft.Container(
                            content=ft.Column([
                                ft.Row([
                                    ft.Text("ID:", weight="bold", size=14),
                                    ft.Text(self.payment_data.id or "N/A", size=14, selectable=True),
                                ]),
                                ft.Row([
                                    ft.Text("Description:", weight="bold", size=14),
                                    ft.Text(self.payment_data.description or "N/A", size=14, expand=True, selectable=True),
                                ]),
                                ft.Row([
                                    ft.Text("Montant:", weight="bold", size=14),
                                    ft.Text(f"{amount:.2f} €", size=16, color=ft.Colors.PRIMARY, weight="bold", selectable=True),
                                ]),
                                # ft.Row([
                                #     ft.Text("Devise:", weight="bold", size=14),
                                #     ft.Text(self.payment_data.currency or "EUR", size=14, selectable=True),
                                # ]),
                                ft.Row([
                                    ft.Icon(ft.Icons.CALENDAR_TODAY, size=16, color=ft.Colors.GREY),
                                    ft.Text(f"Créé le: {created_formatted}", size=14, selectable=True),
                                ]),
                                ft.Row([
                                    ft.Icon(ft.Icons.CHECK_CIRCLE, size=16, color=status_color),
                                    ft.Text(status_text, size=14),
                                ]),
                            ], spacing=8),
                            padding=15,
                        )
                    ),
                    
                    # Payment URL if available
                    ft.Text("Lien de Paiement", size=18, weight=ft.FontWeight.BOLD) if self.payment_data.url else ft.Container(),
                    ft.Card(
                        content=ft.Container(
                            content=ft.Column([
                                ft.Text("URL de paiement:", weight="bold", size=14),
                                ft.Text(self.payment_data.url or "", size=12, selectable=True),
                                ft.ElevatedButton(
                                    "Copier le lien",
                                    icon=ft.Icons.COPY,
                                    on_click=lambda e: self.page.run_task(self.copy_to_clipboard, self.payment_data.url),
                                ) if self.payment_data.url else ft.Container(),
                            ], spacing=8),
                            padding=15,
                        )
                    ) if self.payment_data.url else ft.Container(),
                    
                    # Back button
                    ft.ElevatedButton(
                        "Retour à la liste",
                        icon=ft.Icons.ARROW_BACK,
                        on_click=self.go_back,
                    ),
                ],
                spacing=15,
            )
            
            self.content_container.content.controls.append(details)
        else:
            # Error message
            self.content_container.content.controls.append(
                ft.Text("Paiement non trouvé", size=16, color=ft.Colors.RED)
            )
            self.content_container.content.controls.append(
                ft.ElevatedButton(
                    "Retour à la liste",
                    icon=ft.Icons.ARROW_BACK,
                    on_click=self.go_back,
                )
            )
        
        self.update()
    
    async def copy_to_clipboard(self, text):
        """Copy text to clipboard"""
        if text:
            await ft.Clipboard().set(text)
            
            snack = ft.SnackBar(content=ft.Text("Copié dans le presse-papiers"))
            self.page.overlay.append(snack)
            snack.open = True
            self.page.update()
    
    def go_back(self, e):
        """Go back to payment list"""
        self.page.go("/paiement")
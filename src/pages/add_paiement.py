import flet as ft
import asyncio
from loguru import logger
from fastapi.concurrency import run_in_threadpool

from api_stancer import create_payment_intent, get_customer
try:
    from shared.schemas import PaymentIntentStancerSchema
except ImportError:
    from schemas import PaymentIntentStancerSchema


class Add_Paiement(ft.View):
    def __init__(self, route: str = "/add_paiement", *args, **kwargs):
        super().__init__(
            route="/add_paiement",
            padding=20,
            bgcolor=ft.Colors.BLUE_GREY_800,
            *args, **kwargs
        )
        self.scroll = ft.ScrollMode.AUTO
        
        # Controls
        self.client_name = ft.TextField(
            label="Nom du client *", 
            hint_text="Entrez le nom", 
            width=400,
            border_color=ft.Colors.WHITE54,
            label_style=ft.TextStyle(color=ft.Colors.WHITE70),
            text_style=ft.TextStyle(color=ft.Colors.WHITE),
        )
        
        self.email = ft.TextField(
            label="Email", 
            hint_text="email@example.com", 
            width=400,
            border_color=ft.Colors.WHITE54,
            label_style=ft.TextStyle(color=ft.Colors.WHITE70),
            text_style=ft.TextStyle(color=ft.Colors.WHITE),
        )
        
        # Country code dropdown
        self.country_code = ft.Dropdown(
            label="Indicatif",
            hint_text="Pays",
            width=150,
            value="+33",
            options=[
                ft.dropdown.Option(key="+971", text="🇦🇪 +971"), # AE - Émirats (UAE)
                ft.dropdown.Option(key="+43", text="🇦🇹 +43"),  # AT - Autriche
                ft.dropdown.Option(key="+61", text="🇦🇺 +61"),  # AU - Australie
                ft.dropdown.Option(key="+32", text="🇧🇪 +32"),  # BE - Belgique
                ft.dropdown.Option(key="+55", text="🇧🇷 +55"),  # BR - Brésil
                ft.dropdown.Option(key="+1",  text="🇨🇦 +1"),   # CA - Canada
                ft.dropdown.Option(key="+41", text="🇨🇭 +41"),  # CH - Suisse (Confederatio Helvetica)
                ft.dropdown.Option(key="+86", text="🇨🇳 +86"),  # CN - Chine
                ft.dropdown.Option(key="+49", text="🇩🇪 +49"),  # DE - Allemagne (Deutschland)
                ft.dropdown.Option(key="+45", text="🇩🇰 +45"),  # DK - Danemark
                ft.dropdown.Option(key="+34", text="🇪🇸 +34"),  # ES - Espagne (España)
                ft.dropdown.Option(key="+33", text="🇫🇷 +33"),  # FR - France
                ft.dropdown.Option(key="+44", text="🇬🇧 +44"),  # GB - Royaume-Uni (Great Britain)
                ft.dropdown.Option(key="+353", text="🇮🇪 +353"), # IE - Irlande
                ft.dropdown.Option(key="+39", text="🇮🇹 +39"),  # IT - Italie
                ft.dropdown.Option(key="+81", text="🇯🇵 +81"),  # JP - Japon
                ft.dropdown.Option(key="+31", text="🇳🇱 +31"),  # NL - Pays-Bas (Netherlands)
                ft.dropdown.Option(key="+47", text="🇳🇴 +47"),  # NO - Norvège
                ft.dropdown.Option(key="+48", text="🇵🇱 +48"),  # PL - Pologne
                ft.dropdown.Option(key="+7",  text="🇷🇺 +7"),   # RU - Russie
                ft.dropdown.Option(key="+966", text="🇸🇦 +966"), # SA - Arabie saoudite
                ft.dropdown.Option(key="+46", text="🇸🇪 +46"),  # SE - Suède
                ft.dropdown.Option(key="+1",  text="🇺🇸 +1"),   # US - États-Unis
            ],
            border_color=ft.Colors.WHITE54,
            label_style=ft.TextStyle(color=ft.Colors.WHITE70),
            text_style=ft.TextStyle(color=ft.Colors.WHITE),
        )
        
        self.phone = ft.TextField(
            label="Numéro de téléphone", 
            hint_text="612345678", 
            width=240,
            border_color=ft.Colors.WHITE54,
            label_style=ft.TextStyle(color=ft.Colors.WHITE70),
            text_style=ft.TextStyle(color=ft.Colors.WHITE),
            keyboard_type=ft.KeyboardType.PHONE,
        )
        
        self.amount = ft.TextField(
            label="Montant (€) *", 
            hint_text="100", 
            width=400, 
            keyboard_type=ft.KeyboardType.NUMBER,
            border_color=ft.Colors.WHITE54,
            label_style=ft.TextStyle(color=ft.Colors.WHITE70),
            text_style=ft.TextStyle(color=ft.Colors.WHITE),
        )
        
        self.subject = ft.TextField(
            label="Sujet *", 
            hint_text="Description du paiement", 
            width=400,
            multiline=True,
            min_lines=2,
            max_lines=4,
            border_color=ft.Colors.WHITE54,
            label_style=ft.TextStyle(color=ft.Colors.WHITE70),
            text_style=ft.TextStyle(color=ft.Colors.WHITE),
        )
        
        self.message = ft.Text("", size=14, weight=ft.FontWeight.BOLD)
        
        self.submit_button = ft.ElevatedButton(
            "Créer le paiement",
            on_click=self.submit_payment,
            bgcolor=ft.Colors.GREEN_700,
            color=ft.Colors.WHITE,
            width=400,
        )
        
        self.cancel_button = ft.ElevatedButton(
            "Annuler",
            on_click=lambda _: self.page.go("/paiement"),
            bgcolor=ft.Colors.RED_700,
            color=ft.Colors.WHITE,
            width=400,
        )
        
        # Layout
        self.controls = [
            ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Text(
                            "Nouveau Paiement",
                            size=24,
                            weight=ft.FontWeight.BOLD,
                            color=ft.Colors.WHITE,
                        ),
                        ft.Divider(height=20, color=ft.Colors.WHITE24),
                        
                        ft.Text(
                            "* Champs obligatoires",
                            size=12,
                            color=ft.Colors.WHITE54,
                            italic=True,
                        ),
                        
                        self.client_name,
                        self.email,
                        ft.Row(width=400,
                            controls=[
                                self.country_code,
                                self.phone,
                            ],
                            spacing=10,
                        ),
                        self.amount,
                        self.subject,
                        
                        ft.Container(height=10),
                        self.message,
                        ft.Container(height=10),
                        
                        self.submit_button,
                        self.cancel_button,
                    ],
                    spacing=15,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                padding=30,
                border_radius=10,
                bgcolor=ft.Colors.BLUE_GREY_700,
            )
        ]
    
    def validate_form(self) -> tuple[bool, str]:
        """Validate form inputs
        
        Returns: (is_valid, error_message)
        """
        if not self.client_name.value or not self.client_name.value.strip():
            return False, "Le nom du client est obligatoire"
        
        if not self.amount.value or not self.amount.value.strip():
            return False, "Le montant est obligatoire"
        
        try:
            amount = float(self.amount.value)
            if amount <= 0:
                return False, "Le montant doit être supérieur à 0"
        except ValueError:
            return False, "Le montant doit être un nombre valide"
        
        if not self.subject.value or not self.subject.value.strip():
            return False, "Le sujet est obligatoire"
        
        return True, ""
    
    async def submit_payment(self, e):
        """Submit payment to API"""
        # Validate form
        is_valid, error_msg = self.validate_form()
        if not is_valid:
            self.message.value = error_msg
            self.message.color = ft.Colors.RED
            self.page.update()
            return
        
        # Disable button during submission
        self.submit_button.disabled = True
        self.message.value = "Création en cours..."
        self.message.color = ft.Colors.BLUE
        self.page.update()
        
        try:
            # Combine country code with phone number
            phone_number = ""
            if self.phone.value and self.phone.value.strip():
                phone_number = f"{self.country_code.value}{self.phone.value.strip()}"
            
            email = self.email.value.strip() if self.email.value else None
            
            # Create customer first if we have customer info (requires email or phone)
            customer_id = None
            if self.client_name.value.strip() and (email or phone_number):
                customer = await run_in_threadpool(
                    get_customer,
                    name=self.client_name.value.strip(),
                    email=email,
                    phone=phone_number if phone_number else None,
                )
                if customer:
                    customer_id = customer.id
            
            # Create payment intent (amount in cents)
            amount_cents = int(float(self.amount.value) * 100)
            result: PaymentIntentStancerSchema = await run_in_threadpool(
                create_payment_intent,
                amount=amount_cents,
                description=self.subject.value.strip(),
                customer_id=customer_id,
            )
            
            if result and result.id:
                self.message.value = "Paiement créé avec succès!"
                self.message.color = ft.Colors.GREEN
                self.page.update()
                
                # Wait a moment then navigate to payment detail
                await asyncio.sleep(1)
                self.page.go(f"/paiement/{result.id}")
            else:
                self.message.value = "Erreur lors de la création du paiement"
                self.message.color = ft.Colors.RED
                self.submit_button.disabled = False
                self.page.update()
        
        except Exception as ex:
            logger.error(f"Error submitting payment: {str(ex)}")
            self.message.value = f"Erreur: {str(ex)}"
            self.message.color = ft.Colors.RED
            self.submit_button.disabled = False
            self.page.update()
       
import asyncio
import flet as ft

def goto_reception(e):
    asyncio.create_task(e.page.push_route("/reservation"))

def goto_paiement(e):
    asyncio.create_task(e.page.push_route("/paiement"))
    
def goto_home(e):
    asyncio.create_task(e.page.push_route("/"))

menu = ft.PopupMenuButton(
    key="popup",
    items=[
        ft.PopupMenuItem(content="Home", on_click=goto_home),
        ft.PopupMenuItem(icon=ft.Icons.DESK, content="Réservation", on_click=goto_reception),
        ft.PopupMenuItem(icon=ft.Icons.PAYMENT, content="Lien de paiement", on_click=goto_paiement),
        # ft.PopupMenuItem(
        #     content=ft.Row(
        #         controls=[
        #             ft.Icon(ft.Icons.HOURGLASS_TOP_OUTLINED),
        #             ft.Text("Item with a custom content"),
        #         ]
        #     ),
        #     on_click=lambda _: print("Button with custom content clicked!"),
        # ),
        # ft.PopupMenuItem(),  # divider
        # ft.PopupMenuItem(
        #     content="Checked item",
        #     checked=False
        # ),
    ],
)

appbar = ft.AppBar(
    title=ft.Text("HÔTEL PANORAMA"),
    center_title=True,
    actions=[
        menu
    ]
)

import warnings

from fastapi import FastAPI
from fastapi import Request
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from loguru import logger
import flet as ft
import flet.fastapi as flet_fastapi
from dotenv import load_dotenv

from pages.home import Home_Page
from pages.paiement_detail import Paiement_Detail
from pages.list_paiement import List_Paiements
from pages.add_paiement import Add_Paiement
from pages.reservation import Reservation

warnings.filterwarnings("ignore", category=DeprecationWarning)
load_dotenv()

api = FastAPI()

api.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or specify domains: ["https://yourdomain.com"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

@api.middleware("http")
async def log_headers(request: Request, call_next):
    # Print headers to terminal
    print(f"--- Incoming Request from {request.client.host} ---")
    for name, value in request.headers.items():
        print(f"{name}: {value}")
    print("--------------------------------------------------")
    
    response = await call_next(request)
    return response


def before_main(page: ft.Page):
    page.title = "Hotel Panorama Reservation System"
    page.theme_mode = ft.ThemeMode.LIGHT


async def main(page: ft.Page):
    page.title = "Routes Example"
    page.theme_mode = ft.ThemeMode.LIGHT

    print("Initial route:", page.route)

    async def open_settings(e):
        await page.push_route("/settings")

    def route_change():
        print("Route change:", page.route)
        page.views.clear()
        # BEGIN
        # page.views.append(
        #     # Register_Client_List(route="/")
        #     # Register_Client(route="/new")
        #     Register_Client(route="/tablet", actif=True)
        # )
        logger.debug(f"Route changed to: {page.route}")
        if page.route == "/":
            page.views.append(
                Home_Page(route="/")
            )
        elif page.route == "/paiement":
            page.views.append(
                List_Paiements(route="/paiement")
            )
        elif page.route.startswith("/paiement/"):
            paiement_id = page.route.split("/paiement/")[1]
            page.views.append(
                List_Paiements(route="/paiement")
            )
            page.views.append(
                Paiement_Detail(route=page.route, paiement_id=paiement_id)
            )
        elif page.route == "/add_paiement":
            page.views.append(
                List_Paiements(route="/paiement")
            )
            page.views.append(
                Add_Paiement(route="/add_paiement")
            )
        elif page.route == "/reservation":
            page.views.append(
                Reservation(route="/reservation", actif=False)
            )
        page.update()

    async def view_pop(e):
        if e.view is not None:
            print("View pop:", e.view)
            page.views.remove(e.view)
            top_view = page.views[-1]
            await page.push_route(top_view.route)

    page.on_route_change = route_change
    page.on_view_pop = view_pop

    route_change()


@asynccontextmanager
async def lifespan(app: FastAPI):
    await flet_fastapi.app_manager.start()
    yield
    await flet_fastapi.app_manager.shutdown()

api.router.lifespan_context = lifespan

api.mount(
    "/", flet_fastapi.app(main, before_main),
)

app = api
    
if __name__ == "__main__":
    # ft.run(main, host="0.0.0.0", port=8000)
    ft.run(main)
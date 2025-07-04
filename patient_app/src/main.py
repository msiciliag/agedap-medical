import flet as ft
from app_config import APP_LEVEL_STORAGE_KEYS 
from navigation import route_change_handler, view_pop_handler
from app_init import initialize_application
import logging
logger = logging.getLogger(__name__)

def main(page: ft.Page):
    page.title = "AI HealthVault"
    page.adaptive = True

    for key in APP_LEVEL_STORAGE_KEYS:
        if page.client_storage.contains_key(key):
            page.client_storage.remove(key)

    page.window_width = 390
    page.window_height = 844
    page.window_resizable = False
    page.window_maximizable = False

    page.on_route_change = lambda route_event: route_change_handler(page, route_event.route)
    page.on_view_pop = lambda view_pop_event: view_pop_handler(page, view_pop_event)

    logger.info("App starting...")
    page.go("/login")

if __name__ == "__main__":
    initialize_application()
    
    ft.app(target=main)
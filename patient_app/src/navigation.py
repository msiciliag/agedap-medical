import flet as ft
from app_config import CONFIG_DONE_KEY, SESSION_PATIENT_ID_KEY
from views.login_view import build_login_view
from views.config_view import build_config_view
from views.main_app_view import build_main_app_view
from views.service_view import build_dynamic_service_view
import logging

logger = logging.getLogger(__name__)

def route_change_handler(page: ft.Page, route_str: str):
    logger.info(f"Route change triggered. Current page.route: {page.route}, requested route_str: {route_str}")

    current_views_copy = page.views[:]
    page.views.clear()

    page.views.append(build_login_view(page))

    if route_str == "/login" or route_str == "/" or route_str == "":
        pass
    elif route_str == "/config/initial":
        if not page.client_storage.contains_key(SESSION_PATIENT_ID_KEY):
            logger.error("Redirect: /config/initial needs patient ID, going to /login")
            if page.route != "/login": page.go("/login")
            return 
        page.views.append(build_config_view(page, view_route="/config/initial", is_initial_setup=True))
    elif route_str == "/config/update":
        if not page.client_storage.contains_key(SESSION_PATIENT_ID_KEY) or not page.client_storage.get(CONFIG_DONE_KEY):
            logger.error("Redirect: /config/update needs patient ID and prior config, going to /login")
            if page.route != "/login": page.go("/login")
            return
        page.views.append(build_main_app_view(page)) 
        page.views.append(build_config_view(page, view_route="/config/update", is_initial_setup=False))
    elif route_str == "/main":
        config_done = page.client_storage.get(CONFIG_DONE_KEY)
        patient_selected = page.client_storage.contains_key(SESSION_PATIENT_ID_KEY)
        if not config_done or not patient_selected:
            redirect_route = "/config/initial" if patient_selected else "/login"
            logger.error(f"Redirect: /main needs config ({config_done}) and patient ({patient_selected}), going to {redirect_route}")
            if page.route != redirect_route: page.go(redirect_route)
            return
        page.views.append(build_main_app_view(page))
    elif route_str.startswith("/service/"):
        config_done = page.client_storage.get(CONFIG_DONE_KEY)
        patient_selected = page.client_storage.contains_key(SESSION_PATIENT_ID_KEY)
        if not config_done or not patient_selected:
            redirect_route = "/config/initial" if patient_selected else "/login"
            logger.error(f"Redirect: {route_str} needs config and patient, going to {redirect_route}")
            if page.route != redirect_route: page.go(redirect_route)
            return

        parts = route_str.split("/")
        if len(parts) == 3 and parts[1] == "service":
            service_type = parts[2]
            page.views.append(build_main_app_view(page)) 
            page.views.append(build_dynamic_service_view(page, service_type))
        else:
            logger.error(f"Malformed service route: {route_str}. Forcing navigation to /main.")
            page.views.append(build_main_app_view(page))
            if page.route != "/main": page.go("/main") 
            return
    else:
        logger.error(f"Unknown route: {route_str}. Forcing navigation to /login.")
        if page.route != "/login":
            page.go("/login")
        return 

    if len(page.views) != len(current_views_copy) or \
       any(v.route != cv.route for v, cv in zip(page.views, current_views_copy) if hasattr(v, 'route') and hasattr(cv, 'route')):
        logger.info(f"Views updated by route_change. Stack: {[v.route for v in page.views if hasattr(v, 'route')]}")
        page.update()
    else:
        logger.info(f"Views unchanged by route_change or routes are the same. Stack: {[v.route for v in page.views if hasattr(v, 'route')]}")

def view_pop_handler(page: ft.Page, view_popped_event: ft.ViewPopEvent): 
    page.views.pop()
    if not page.views:
        logger.info("View stack empty after pop, going to login.")
        page.go("/login")
    else:
        top_view = page.views[-1]
        logger.info(f"Popped view. Navigating back to: {top_view.route}")
        page.go(top_view.route)
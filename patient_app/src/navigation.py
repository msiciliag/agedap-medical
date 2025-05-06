import flet as ft
from app_config import CONFIG_DONE_KEY, SESSION_PATIENT_ID_KEY
from views.login_view import build_login_view
from views.config_view import build_config_view
from views.main_app_view import build_main_app_view

def route_change_handler(page: ft.Page, route_str: str):
    print(f"Route change triggered. Current page.route: {page.route}, requested route_str: {route_str}")
    
    current_views_copy = page.views[:]  
    page.views.clear()

    page.views.append(build_login_view(page))

    if route_str == "/login" or route_str == "/" or route_str == "":
        pass
    elif route_str == "/config/initial":
        if not page.client_storage.contains_key(SESSION_PATIENT_ID_KEY):
            print("Redirect: /config/initial needs patient ID, going to /login")
            if page.route != "/login": page.go("/login")
            return 
        page.views.append(build_config_view(page, view_route="/config/initial", is_initial_setup=True))
    elif route_str == "/config/update":
        if not page.client_storage.contains_key(SESSION_PATIENT_ID_KEY) or not page.client_storage.get(CONFIG_DONE_KEY):
            print("Redirect: /config/update needs patient ID and prior config, going to /login")
            if page.route != "/login": page.go("/login")
            return
        page.views.append(build_main_app_view(page))
        page.views.append(build_config_view(page, view_route="/config/update", is_initial_setup=False))
    elif route_str == "/main":
        config_done = page.client_storage.get(CONFIG_DONE_KEY)
        patient_selected = page.client_storage.contains_key(SESSION_PATIENT_ID_KEY)
        if not config_done or not patient_selected:
            redirect_route = "/config/initial" if patient_selected else "/login"
            print(f"Redirect: /main needs config ({config_done}) and patient ({patient_selected}), going to {redirect_route}")
            if page.route != redirect_route: page.go(redirect_route)
            return
        page.views.append(build_main_app_view(page))
    elif route_str.startswith("/service/"):
        print(f"Notice: Service route {route_str} hit. No specific view defined. Defaulting to login page if no other match.")
        if page.route != "/login": page.go("/login") 
        return
    else: # Unknown route
        print(f"Unknown route: {route_str}. Forcing navigation to /login.")
        if page.route != "/login":
            page.go("/login")
        return 

    if len(page.views) != len(current_views_copy) or \
       any(v.route != cv.route for v, cv in zip(page.views, current_views_copy) if hasattr(v, 'route') and hasattr(cv, 'route')):
        print(f"Views updated by route_change. Stack: {[v.route for v in page.views if hasattr(v, 'route')]}")
        page.update()
    else:
        print(f"Views unchanged by route_change or routes are the same. Stack: {[v.route for v in page.views if hasattr(v, 'route')]}")


def view_pop_handler(page: ft.Page, view_popped_event: ft.ViewPopEvent): 
    page.views.pop()
    if not page.views:
        print("View stack empty after pop, going to login.")
        page.go("/login")
    else:
        top_view = page.views[-1]
        print(f"Popped view. Navigating back to: {top_view.route}")
        page.go(top_view.route)
import flet as ft
from api_client.base_client import BaseClient
from app_config import SERVICE_CONFIGS

def build_dynamic_service_view(page: ft.Page, service_key: str):
    """
    Dynamically builds the service view by fetching additional info from the service endpoint.
    """
    service_config = SERVICE_CONFIGS.get(service_key)
    if not service_config:
        return ft.View(
            f"/service/{service_key}", 
            [
                ft.AppBar(title=ft.Text("Error"), bgcolor=ft.Colors.SURFACE_TINT),
                ft.Text(f"Configuration for service '{service_key}' not found."),
                ft.ElevatedButton("Back to Services", on_click=lambda _: page.go("/main"))
            ]
        )
    
    service_name = service_key
    description = "Loading service details..."
    content_controls = [
        ft.Text(description)
    ]

    try:
        client = BaseClient(
            service_config["url"],
            fhe_directory=service_config["fhe_directory"],
            key_directory=service_config["key_directory"]
        )
        info = client.request_additional_info()
        service_name = info.get("service_name", service_key)
        description = info.get("description", "No description available.")
        content_controls = [
            ft.Text(service_name, size=24, weight=ft.FontWeight.BOLD),
            ft.Text(description),
        ]
    except ValueError:
        description = f"Error: Invalid response format from {service_name} service."
        content_controls = [ft.Text(description)]
    
    view_content = [
        ft.AppBar(title=ft.Text(service_name), bgcolor=ft.Colors.SURFACE_TINT),
        ft.Container(
            content=ft.Column(
                controls=content_controls + [ft.ElevatedButton("Back to Services", on_click=lambda _: page.go("/main"))],
                spacing=20
            ),
            padding=20,
            expand=True
        )
    ]
    
    return ft.View(
        f"/service/{service_key}",
        view_content
    )
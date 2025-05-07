import flet as ft
import requests
from app_config import SERVICE_ENDPOINTS

def build_dynamic_service_view(page: ft.Page, service_type: str):
    """
    Dynamically builds the service view by fetching additional info from the service endpoint.
    """
    endpoint = SERVICE_ENDPOINTS.get(service_type)
    if not endpoint:
        return ft.View(
            f"/service/{service_type}", 
            [
                ft.AppBar(title=ft.Text("Error"), bgcolor=ft.Colors.SURFACE_TINT),
                ft.Text(f"Configuration for service '{service_type}' not found."),
                ft.ElevatedButton("Back to Services", on_click=lambda _: page.go("/main"))
            ]
        )
    
    service_name = service_type
    description = "Loading service details..."
    content_controls = [
        ft.Text(description) # Placeholder
    ]

    try:
        response = requests.get(endpoint, timeout=5)
        response.raise_for_status()
        info = response.json()
        service_name = info.get("service_name", service_type)
        description = info.get("description", "No description available.")
        # Update content_controls with actual data
        content_controls = [
            ft.Text(service_name, size=24, weight=ft.FontWeight.BOLD),
            ft.Text(description),
            # Add other service-specific controls here if needed
        ]
    except requests.exceptions.Timeout:
        description = f"Error: Timeout connecting to {service_name} service."
        content_controls = [ft.Text(description)]
    except requests.exceptions.HTTPError as e:
        description = f"Error: {service_name} service returned HTTP {e.response.status_code}."
        content_controls = [ft.Text(description)]
    except requests.exceptions.RequestException as e:
        description = f"Error: Could not connect to {service_name} service. {e}"
        content_controls = [ft.Text(description)]
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
        f"/service/{service_type}",
        view_content
    )
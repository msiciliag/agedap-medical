import flet as ft
from datetime import date
from app_config import (
    CONFIG_DONE_KEY, NAME_KEY, SESSION_PATIENT_ID_KEY, SERVICE_CONFIGS, APP_LEVEL_STORAGE_KEYS
)
from api_client.base_client import BaseClient
from utils import db, omop

def build_services_page_content(page: ft.Page):
    service_tiles = []
    for service_key, service_details in SERVICE_CONFIGS.items():
        service_name = service_key
        description = "Could not load service information." 
        try:
            
            client = BaseClient(
                service_details["url"],
                fhe_directory=service_details["fhe_directory"],
                key_directory=service_details["key_directory"]
            )
            info = client.request_additional_info()
            service_name = info.get("service_name", service_key)
            description = info.get("description", "No description provided.")  
            service_tiles.append(
                ft.ListTile(
                    leading=ft.Icon(ft.Icons.HEALTH_AND_SAFETY),
                    title=ft.Text(service_name, weight=ft.FontWeight.BOLD),
                    subtitle=ft.Text(description),
                    on_click=lambda _, st=service_key: page.go(f"/service/{st}")
                )
            )
        except ValueError:  
            description = f"Error: Invalid response format from {service_key} service."
        except Exception as e:
            print(f"An unexpected error occurred with {service_key} service: {e}, possibly due to network issues or service unavailability.")
            description = f"Error: An unexpected issue occurred with {service_key} service, possibly due to network issues or service unavailability."
        

    return [
        ft.Text("Available AI Services", size=24, weight=ft.FontWeight.BOLD),
        ft.Column(service_tiles, spacing=10)
    ]


def build_my_data_page_content(page: ft.Page): 
    session_patient_id = page.client_storage.get(SESSION_PATIENT_ID_KEY) or "Unknown"
    if not page.client_storage.get(CONFIG_DONE_KEY):
        return [
            ft.Text("My Data", size=24, weight=ft.FontWeight.BOLD),
            ft.Text(f"Please complete the configuration for Patient ID {session_patient_id} to load data."),
            ft.ElevatedButton("Go to Configuration", on_click=lambda _: page.go("/config/initial"), icon=ft.Icons.SETTINGS)
        ]
    else:
        dob_display = db.get_date_of_birth(session_patient_id) or "N/A"
        divider_color = ft.Colors.with_opacity(0.5, ft.Colors.ON_SURFACE)
        session_patient_id = page.client_storage.get(SESSION_PATIENT_ID_KEY) or "Unknown"
        current_name = page.client_storage.get(NAME_KEY) or "N/A"
        gender = db.get_gender(session_patient_id) or "N/A"

        return [
            ft.Row([
                ft.Text("My Data", size=24, weight=ft.FontWeight.BOLD),
                ft.Text(f"(Patient ID: {session_patient_id})", size=12, italic=True, color=ft.Colors.ON_SURFACE_VARIANT)
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Card(
                content=ft.Container(
                    padding=ft.padding.all(15),
                    content=ft.Column(
                        [
                            ft.Row([
                                ft.Text("Name:", weight=ft.FontWeight.BOLD, width=100),
                                ft.Text(current_name)
                            ]),
                            ft.Divider(height=1, color=divider_color),
                            ft.Row([
                                ft.Text("Date of Birth:", weight=ft.FontWeight.BOLD, width=100),
                                ft.Text(dob_display)
                            ]),
                            ft.Divider(height=1, color=divider_color),
                            ft.Row([
                                ft.Text("Gender:", weight=ft.FontWeight.BOLD, width=100),
                                ft.Text(gender)
                            ]),
                        ],
                        spacing=10
                    )
                )
            )
        ]

def build_main_app_view(page: ft.Page):
    main_content_area = ft.Container(
        content=None, 
        expand=True,
        alignment=ft.alignment.top_center,
        padding=ft.padding.all(20)
    )

    def update_content(selected_index):
        content_column = None
        current_alignment = ft.MainAxisAlignment.START

        if selected_index == 0: 
            content_column = ft.Column(
                build_services_page_content(page),
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=current_alignment,
                spacing=10
            )
        elif selected_index == 1: # My Data
            content_column = ft.Column(
                build_my_data_page_content(page), 
                horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
                alignment=current_alignment,
                spacing=15
            )
        elif selected_index == 2:
            content_column = ft.Column(
                [
                    ft.Text("Configuration", size=24, weight=ft.FontWeight.BOLD),
                    ft.ElevatedButton(
                        "Update My Data",
                        on_click=lambda _: page.go("/config/update"),
                        icon=ft.Icons.CLOUD_SYNC
                    )
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=current_alignment,
                spacing=10
            )
        main_content_area.content = content_column
        main_content_area.update()

    def on_navigation_change(e):
        update_content(e.control.selected_index)

    main_content_area.content = ft.Column(
        build_services_page_content(page),
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        alignment=ft.MainAxisAlignment.START,
        spacing=10
    )
    
    def logout(e):
        for key in APP_LEVEL_STORAGE_KEYS: 
            if page.client_storage.contains_key(key):
                page.client_storage.remove(key)
        db.clear_database()
        omop.load_custom_concepts_from_definitions()
        page.go("/login")
    
    return ft.View(
        "/main",
        [
            main_content_area
        ],
        appbar=ft.AppBar(
            title=ft.Text("AI HealthVault"),
            bgcolor=ft.Colors.SURFACE_TINT,
            actions=[
                ft.IconButton(
                    icon=ft.Icons.LOGOUT,
                    tooltip="Logout and delete data",
                    on_click=logout
                )
            ],
            automatically_imply_leading=False
        ),
        navigation_bar=ft.NavigationBar(
            destinations=[
                ft.NavigationBarDestination(icon=ft.Icons.MEDICAL_SERVICES_OUTLINED, selected_icon=ft.Icons.MEDICAL_SERVICES, label="AI Services"),
                ft.NavigationBarDestination(icon=ft.Icons.PERSON_OUTLINE, selected_icon=ft.Icons.PERSON, label="My Data"),
                ft.NavigationBarDestination(icon=ft.Icons.SETTINGS_OUTLINED, selected_icon=ft.Icons.SETTINGS, label="Configuration"),
            ],
            selected_index=0, 
            on_change=on_navigation_change,
        ),
    )
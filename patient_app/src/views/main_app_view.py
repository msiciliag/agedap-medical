import flet as ft
from datetime import date
from app_config import (
    CONFIG_DONE_KEY, NAME_KEY, DOB_KEY, GENDER_KEY, SESSION_PATIENT_ID_KEY,
    APP_LEVEL_STORAGE_KEYS
)

def build_services_page_content(page: ft.Page):
    def handle_service_click(service_name):
        page.go(f"/service/{service_name}")

    services = [
        {"name": "Breast Cancer Screening", "description": "AI-assisted mammogram analysis."},
        {"name": "Diabetes Risk Assessment", "description": "Predicting diabetes risk using patient data."},
    ]

    service_tiles = [
        ft.ListTile(
            leading=ft.Icon(ft.Icons.HEALTH_AND_SAFETY),
            title=ft.Text(service["name"], weight=ft.FontWeight.BOLD),
            subtitle=ft.Text(service["description"]),
            on_click=lambda _, s=service["name"]: handle_service_click(s)
        )
        for service in services
    ]

    return [
        ft.Text("Available AI Services", size=24, weight=ft.FontWeight.BOLD),
        ft.Column(service_tiles, spacing=10)
    ]

def build_my_data_page_content(page: ft.Page): 
    if not page.client_storage.get(CONFIG_DONE_KEY):
        session_patient_id = page.client_storage.get(SESSION_PATIENT_ID_KEY) or "Unknown"
        return [
            ft.Text("My Data", size=24, weight=ft.FontWeight.BOLD),
            ft.Text(f"Please complete the configuration for Patient ID {session_patient_id} to load data."),
            ft.ElevatedButton("Go to Configuration", on_click=lambda _: page.go("/config/initial"), icon=ft.Icons.SETTINGS)
        ]
    else:
        dob_str = page.client_storage.get(DOB_KEY)
        dob_display = "N/A"
        if dob_str:
            try:
                dob_date = date.fromisoformat(dob_str)
                dob_display = dob_date.strftime("%B %d, %Y")
            except (ValueError, TypeError):
                dob_display = "Invalid Date Format"

        divider_color = ft.Colors.with_opacity(0.5, ft.Colors.ON_SURFACE)
        session_patient_id = page.client_storage.get(SESSION_PATIENT_ID_KEY) or "Unknown"
        current_name = page.client_storage.get(NAME_KEY) or "N/A" 
        gender = page.client_storage.get(GENDER_KEY) or "N/A"

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
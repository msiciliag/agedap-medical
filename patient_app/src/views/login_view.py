import flet as ft
from app_config import (
    USER_PATIENT_IDS, CONFIG_DONE_KEY, NAME_KEY, DOB_KEY, GENDER_KEY,
    SESSION_PATIENT_ID_KEY, SESSION_HOSPITAL_URL_KEY, SESSION_HOSPITAL_NAME_KEY
)

def build_login_view(page: ft.Page):
    def handle_patient_selection(selected_id):
        keys_to_clear_on_login = [
            CONFIG_DONE_KEY, NAME_KEY, DOB_KEY, GENDER_KEY,
            SESSION_HOSPITAL_URL_KEY, SESSION_HOSPITAL_NAME_KEY
        ]
        for key in keys_to_clear_on_login:
            if page.client_storage.contains_key(key):
                page.client_storage.remove(key)

        page.client_storage.set(SESSION_PATIENT_ID_KEY, selected_id)
        page.go("/config/initial")

    patient_tiles = []
    for name, patient_id in USER_PATIENT_IDS.items():
        current_id = patient_id
        tile = ft.ListTile(
            leading=ft.Icon(ft.Icons.ACCOUNT_CIRCLE_OUTLINED),
            title=ft.Text(name.capitalize()),
            subtitle=ft.Text(f"ID: {patient_id}"),
            hover_color=ft.Colors.with_opacity(0.1, ft.Colors.PRIMARY),
            on_click=lambda _, pid=current_id: handle_patient_selection(pid)
        )
        patient_tiles.append(tile)

    if not patient_tiles:
        patient_content = ft.Text("No patients configured in USER_PATIENT_IDS.")
    else:
        patient_content = ft.Column(
            patient_tiles,
            spacing=5,
        )

    return ft.View(
        "/login",
        [
            ft.AppBar(title=ft.Text("AI HealthVault"), bgcolor=ft.Colors.SURFACE_TINT),
            ft.Column(
                [
                    ft.Icon(name=ft.Icons.MEDICAL_INFORMATION_OUTLINED, size=100, color=ft.Colors.PRIMARY),
                    ft.Container(height=10),
                    ft.Text("Select patient profile:", size=16, weight=ft.FontWeight.W_500),
                    ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
                    ft.Container(
                       content=patient_content,
                    )
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=15,
            )
        ],
        padding=ft.padding.all(20),
        vertical_alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    )
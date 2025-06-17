import flet as ft
from datetime import date
from app_config import (
    HOSPITAL_LIST, CONFIG_DONE_KEY, SESSION_PATIENT_ID_KEY, 
    SESSION_HOSPITAL_NAME_KEY, SESSION_HOSPITAL_URL_KEY, NAME_KEY
)
from utils import fhir, db
from utils.data_mapper import transform_patient

def build_config_page_content(page: ft.Page, is_initial_setup=False):
    session_patient_id = page.client_storage.get(SESSION_PATIENT_ID_KEY)
    if not session_patient_id:
        return [ft.Text("Error: No patient selected. Please log in again.", color=ft.Colors.RED)]

    status_text = ft.Text()
    
    def get_options_for_dropdown(): 
        options = []
        for name, url in HOSPITAL_LIST.items():
            options.append(ft.dropdown.Option(key=name, text=name))
        return options

    save_button = ft.ElevatedButton(
        text="Download My Data" if is_initial_setup else "Update My Data",
        on_click=None,
        icon=ft.Icons.CLOUD_DOWNLOAD if is_initial_setup else ft.Icons.CLOUD_SYNC,
        disabled=True
    )

    def on_dropdown_change(e):
        save_button.disabled = not hospital_dropdown.value
        page.update()

    current_hospital = page.client_storage.get(SESSION_HOSPITAL_NAME_KEY) if not is_initial_setup else None

    hospital_dropdown = ft.Dropdown(
        options=get_options_for_dropdown(),
        hint_text="Select a hospital",
        on_change=on_dropdown_change,
        value=current_hospital
    )
    save_button.disabled = not hospital_dropdown.value 

    def save_button_click(e):
        current_patient_id = session_patient_id 
        selected_hospital_name = hospital_dropdown.value

        if not selected_hospital_name:
            status_text.value = "Please select a hospital first."
            status_text.color = ft.Colors.AMBER
            page.update()
            return

        status_text.value = "Fetching data..."
        status_text.color = ft.Colors.BLUE
        save_button.disabled = True
        page.update()

        url = HOSPITAL_LIST[selected_hospital_name]

        try:
            patient = fhir.get_patient_data(current_patient_id, url)

            if patient is None:
                status_text.value = f"Error: Could not find patient with ID {current_patient_id} at {selected_hospital_name}."
                status_text.color = ft.Colors.RED
                save_button.disabled = False
                page.update()
                return
            print(f"Fetched patient: {patient} from {selected_hospital_name}")
            patient_data = fhir.get_patient_data_dict(patient)
            print(f"Fetched patient data: {patient_data}")
            #the date comes like this : {'name': 'Alice Smith', 'date_of_birth': datetime.date(1985, 5, 15), 'gender': 'female'}
            dob = patient_data.get("date_of_birth")
            if isinstance(dob, date):
                patient_data["date_of_birth"] = dob.isoformat()
            dob_split = patient_data.get("date_of_birth", "").split("-")

            page.client_storage.set(CONFIG_DONE_KEY, True)
            page.client_storage.set(SESSION_HOSPITAL_NAME_KEY, selected_hospital_name)
            page.client_storage.set(SESSION_HOSPITAL_URL_KEY, url)
            page.client_storage.set(NAME_KEY, patient_data.get("name", "N/A"))

            print(f"Saving patient data: {patient_data}")
            omop_person = transform_patient(patient_data, current_patient_id)
            db.create_or_update_person(omop_person)

            page.go("/main")

        except Exception as ex:
            print(f"Error fetching or saving patient data: {ex}")
            status_text.value = f"Error: An unexpected error occurred. Check logs."
            status_text.color = ft.Colors.RED
            save_button.disabled = False
            page.update()

    save_button.on_click = save_button_click

    note_color = ft.Colors.with_opacity(0.7, ft.Colors.ON_SURFACE)
    patient_name_display = page.client_storage.get(NAME_KEY) or "N/A"
    
    return [
        ft.Column(
            [
                ft.Text("Select your Hospital", size=24, weight=ft.FontWeight.BOLD),
                ft.Text(f"Patient ID: {session_patient_id}{f', {patient_name_display}' if patient_name_display else ''}."),
                ft.Divider(height=10, color=ft.colors.TRANSPARENT),
                hospital_dropdown,
                ft.Text(
                    "*Your medical data will be stored locally for this session.",
                    italic=True, size=12, color=note_color
                ),
                ft.Container(height=10),
                save_button,
                status_text,
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10,
        )
    ]

def build_config_view(page: ft.Page, view_route: str, is_initial_setup: bool):
    title = "Initial Configuration" if is_initial_setup else "Update Configuration"
    return ft.View(
        view_route,
        [
            ft.AppBar(
                title=ft.Text(title),
                bgcolor=ft.Colors.SURFACE_TINT,
                automatically_imply_leading=True 
            ),
            ft.Container(
                content=ft.Column(
                    build_config_page_content(page, is_initial_setup=is_initial_setup),
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    scroll=ft.ScrollMode.ADAPTIVE
                ),
                expand=True,
                padding=ft.padding.all(20),
                alignment=ft.alignment.top_center
            )
        ],
    )
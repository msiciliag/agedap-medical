import flet as ft
from datetime import date

STORAGE_PREFIX = "agedap.medical."
CONFIG_DONE_KEY = f"{STORAGE_PREFIX}config_done"
NAME_KEY = f"{STORAGE_PREFIX}name"
DOB_KEY = f"{STORAGE_PREFIX}date_of_birth"
GENDER_KEY = f"{STORAGE_PREFIX}gender"
SESSION_PATIENT_ID_KEY = f"{STORAGE_PREFIX}session_patient_id"
SESSION_HOSPITAL_URL_KEY = f"{STORAGE_PREFIX}hospital_url"
SESSION_HOSPITAL_NAME_KEY = f"{STORAGE_PREFIX}hospital_name"

USER_PATIENT_IDS = {
    "alice": "758718",
    "john": "35552",
}

HOSPITAL_LIST = {
    "Hospital Universitario Ramón Y Cajal": 'https://hapi.fhir.org/baseR5',
    "Hospital Universitario 12 de Octubre": 'https://hapi.fhir.org/baseR5',
}


def main(page: ft.Page):
    page.title = "AI HealthVault"
    page.adaptive = True

    keys_to_clear = [
        CONFIG_DONE_KEY, NAME_KEY, DOB_KEY, GENDER_KEY,
        SESSION_PATIENT_ID_KEY, SESSION_HOSPITAL_URL_KEY, SESSION_HOSPITAL_NAME_KEY
    ]
    for key in keys_to_clear:
        if page.client_storage.contains_key(key):
            page.client_storage.remove(key)

    page.window_width = 390
    page.window_height = 844
    page.window_resizable = False
    page.window_maximizable = False

    def build_services_page_content():
        name = page.client_storage.get(NAME_KEY) or "User"
        return [
            ft.Text(f"Welcome {name}", size=24, weight=ft.FontWeight.BOLD),
            ft.Text("There are no private AI services available at the moment for you.")
        ]

    def build_my_data_page_content():
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
            name = page.client_storage.get(NAME_KEY) or "N/A"
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
                                    ft.Text(name)
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

    def build_config_page_content(is_initial_setup=False):
        session_patient_id = page.client_storage.get(SESSION_PATIENT_ID_KEY)
        if not session_patient_id:
             return [ft.Text("Error: No patient selected. Please log in again.", color=ft.Colors.RED)]

        def get_options():
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

        status_text = ft.Text()

        def on_dropdown_change(e):
            save_button.disabled = not hospital_dropdown.value
            page.update()

        current_hospital = page.client_storage.get(SESSION_HOSPITAL_NAME_KEY) if not is_initial_setup else None

        hospital_dropdown = ft.Dropdown(
            options=get_options(),
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
                patient = fhir_utils.get_patient_data(int(current_patient_id), url)

                if patient is None:
                    status_text.value = f"Error: Could not find patient with ID {current_patient_id} at {selected_hospital_name}."
                    status_text.color = ft.Colors.RED
                    save_button.disabled = False
                    page.update()
                    return

                patient_data = fhir_utils.get_patient_data_dict(patient)

                page.client_storage.set(NAME_KEY, patient_data["name"])
                dob_iso = patient_data["date_of_birth"].isoformat() if patient_data.get("date_of_birth") else None
                if dob_iso:
                    page.client_storage.set(DOB_KEY, dob_iso)
                elif page.client_storage.contains_key(DOB_KEY):
                    page.client_storage.remove(DOB_KEY)

                page.client_storage.set(GENDER_KEY, patient_data["gender"])
                page.client_storage.set(CONFIG_DONE_KEY, True)
                page.client_storage.set(SESSION_HOSPITAL_NAME_KEY, selected_hospital_name)
                page.client_storage.set(SESSION_HOSPITAL_URL_KEY, url)

                page.go("/main")

            except Exception as ex:
                print(f"Error fetching or saving patient data: {ex}")
                status_text.value = f"Error: An unexpected error occurred."
                status_text.color = ft.Colors.RED
                save_button.disabled = False
                page.update()

        save_button.on_click = save_button_click

        note_color = ft.Colors.with_opacity(0.7, ft.Colors.ON_SURFACE)
        name = page.client_storage.get(NAME_KEY)
        return [
            ft.Column(
                [
                    ft.Text("Select your Hospital", size=24, weight=ft.FontWeight.BOLD),
                    ft.Text(f"Patient ID: {session_patient_id}{f', {name}' if name else ''}."),
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

    def build_login_view():
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

    def build_config_view(view_route: str, is_initial_setup: bool):
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
                        build_config_page_content(is_initial_setup=is_initial_setup),
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        scroll=ft.ScrollMode.ADAPTIVE
                    ),
                    expand=True,
                    padding=ft.padding.all(20),
                    alignment=ft.alignment.top_center
                )
            ],
        )

    def build_main_app_view():
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
                    build_services_page_content(),
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    alignment=current_alignment,
                    spacing=10
                )
            elif selected_index == 1:
                 content_column = ft.Column(
                    build_my_data_page_content(),
                     horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
                     alignment=current_alignment,
                     spacing=15
                 )
            elif selected_index == 2:
                 session_patient_id = page.client_storage.get(SESSION_PATIENT_ID_KEY) or "Unknown"
                 name = page.client_storage.get(NAME_KEY) or "Patient"
                 content_column = ft.Column(
                    [
                        ft.Text("Configuration", size=24, weight=ft.FontWeight.BOLD),
                        ft.ElevatedButton(
                            "Update My Data",
                            on_click=lambda _: page.go("/config/update"),
                            icon=ft.Icons.CLOUD_DOWNLOAD
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

        initial_content_column = ft.Column(
             build_services_page_content(),
             horizontal_alignment=ft.CrossAxisAlignment.CENTER,
             alignment=ft.MainAxisAlignment.START,
             spacing=10
         )
        main_content_area.content = initial_content_column

        def logout(e):
            for key in keys_to_clear:
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

    def route_change(route):
        current_views = page.views[:]
        page.views.clear()

        page.views.append(build_login_view())

        if page.route == "/login" or page.route == "/" or page.route == "":
             pass
        elif page.route == "/config/initial":
            if not page.client_storage.contains_key(SESSION_PATIENT_ID_KEY):
                 print("Redirect: /config/initial needs patient ID, going to /login")
                 page.views.clear()
                 page.views.append(build_login_view())
                 page.go("/login")
                 return
            page.views.append(build_config_view(view_route="/config/initial", is_initial_setup=True))
        elif page.route == "/config/update":
             if not page.client_storage.contains_key(SESSION_PATIENT_ID_KEY) or not page.client_storage.get(CONFIG_DONE_KEY):
                 print("Redirect: /config/update needs patient ID and prior config, going to /login")
                 page.views.clear()
                 page.views.append(build_login_view())
                 page.go("/login") 
                 return
             page.views.append(build_main_app_view())
             page.views.append(build_config_view(view_route="/config/update", is_initial_setup=False))
        elif page.route == "/main":
            config_done = page.client_storage.get(CONFIG_DONE_KEY)
            patient_selected = page.client_storage.contains_key(SESSION_PATIENT_ID_KEY)

            if not config_done or not patient_selected:
                 print(f"Redirect: /main needs config ({config_done}) and patient ({patient_selected}), going back")
                 redirect_route = "/config/initial" if patient_selected else "/login"
                 page.go(redirect_route)
                 return
            else:
                 page.views.append(build_main_app_view())
        else:
             print(f"Unknown route: {page.route}. Going to /login.")
             page.go("/login")
             return

        if len(page.views) != len(current_views) or any(v.route != cv.route for v, cv in zip(page.views, current_views)):
             print(f"Views updated. Stack: {[v.route for v in page.views]}")
             page.update()
        else:
             print(f"Views unchanged. Stack: {[v.route for v in page.views]}")


    def view_pop(view):
        page.views.pop()
        if not page.views:
            print("View stack empty after pop, going to login.")
            page.go("/login")
        else:
            top_view = page.views[-1]
            print(f"Popped view. Navigating back to: {top_view.route}")
            page.go(top_view.route)

    page.on_route_change = route_change
    page.on_view_pop = view_pop

    print("App starting...")
    page.go("/login")

    print("Warning: fhir_utils not found. Using dummy implementation.")
    class DummyPatientData:
        def __init__(self, name, dob, gender):
            self.name = name
            self.date_of_birth = dob
            self.gender = gender

    class DummyFhirUtils:
        def get_patient_data(self, patient_id, url):
            print(f"Dummy fetch for patient {patient_id} at {url}")
            if str(patient_id) == "758718": 
                return DummyPatientData("Alice Smith", date(1985, 5, 15), "female")
            elif str(patient_id) == "35552": 
                return DummyPatientData("John Doe", date(1970, 10, 20), "male")
            else:
                return None 

        def get_patient_data_dict(self, patient):
            if patient:
                return {
                    "name": patient.name,
                    "date_of_birth": patient.date_of_birth,
                    "gender": patient.gender
                }
            return {}
    fhir_utils = DummyFhirUtils()

ft.app(target=main)
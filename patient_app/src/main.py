# import flet as ft
import flet as ft
import fhir_utils  # Assuming fhir_utils.py exists and works as before
from datetime import date

# Define the storage prefix globally for consistency
STORAGE_PREFIX = "agedap.medical."
# Define keys for client storage
CONFIG_DONE_KEY = f"{STORAGE_PREFIX}config_done"
NAME_KEY = f"{STORAGE_PREFIX}name"
DOB_KEY = f"{STORAGE_PREFIX}date_of_birth"
GENDER_KEY = f"{STORAGE_PREFIX}gender"
SESSION_PATIENT_ID_KEY = f"{STORAGE_PREFIX}session_patient_id"

# --- Define User-to-ID Mapping ---
USER_PATIENT_IDS = {
    "alice": "758718",
    "john": "35552"
}

# Define the default Hospital URL
DEFAULT_HOSPITAL_URL = 'https://hapi.fhir.org/baseR5'
DEFAULT_HOSPITAL_NAME = "HAPI Sandbox"


def main(page: ft.Page):
    page.title = "External Medical Service"
    page.adaptive = True # Keep adaptive for native look/feel

    # --- Clear storage keys on startup ---
    print("Clearing stored keys on startup...")
    keys_to_clear = [
        CONFIG_DONE_KEY, NAME_KEY, DOB_KEY, GENDER_KEY,
        SESSION_PATIENT_ID_KEY
    ]
    for key in keys_to_clear:
        if page.client_storage.contains_key(key):
            page.client_storage.remove(key)
    print("Keys cleared.")
    # --- End clearing storage ---

    # --- Set window size and properties ---
    page.window_width = 390
    page.window_height = 844
    page.window_resizable = False
    page.window_maximizable = False
    # --- End window settings ---


    # --- Page Content Building Functions ---
    # (build_services_page_content, build_my_data_page_content, build_config_page_content remain the same)
    def build_services_page_content():
        """Builds the content controls for the Services page."""
        return [
            ft.Text("Services", size=24, weight=ft.FontWeight.BOLD),
            ft.Text("Service functionality not yet implemented.")
        ]

    def build_my_data_page_content():
        """Builds the content controls for the My Data page."""
        if not page.client_storage.get(CONFIG_DONE_KEY):
             session_patient_id = page.client_storage.get(SESSION_PATIENT_ID_KEY) or "Unknown"
             return [
                ft.Text("My Data", size=24, weight=ft.FontWeight.BOLD),
                ft.Text(f"Please complete the configuration for Patient ID {session_patient_id} to load data."),
                ft.ElevatedButton("Go to Configuration", on_click=lambda _: page.go("/config/initial"), icon=ft.Icons.SETTINGS)
             ]
        else:
            dob_str = page.client_storage.get(DOB_KEY)
            try:
                dob_date = date.fromisoformat(dob_str)
                dob_display = dob_date.strftime("%B %d, %Y")
            except (ValueError, TypeError):
                dob_display = dob_str

            divider_color = ft.colors.with_opacity(0.5, ft.Colors.ON_SURFACE)
            session_patient_id = page.client_storage.get(SESSION_PATIENT_ID_KEY) or "Unknown"

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
                                    ft.Text(page.client_storage.get(NAME_KEY) or "N/A")
                                ]),
                                ft.Divider(height=1, color=divider_color),
                                ft.Row([
                                    ft.Text("Date of Birth:", weight=ft.FontWeight.BOLD, width=100),
                                    ft.Text(dob_display)
                                ]),
                                ft.Divider(height=1, color=divider_color),
                                ft.Row([
                                    ft.Text("Gender:", weight=ft.FontWeight.BOLD, width=100),
                                    ft.Text(page.client_storage.get(GENDER_KEY) or "N/A")
                                ]),
                            ],
                            spacing=10
                        )
                    )
                )
            ]

    def build_config_page_content(is_initial_setup=False):
        """Builds the content controls for the Configuration page."""
        session_patient_id = page.client_storage.get(SESSION_PATIENT_ID_KEY)
        if not session_patient_id:
             return [ft.Text("Error: No patient selected. Please log in again.", color=ft.Colors.RED)]

        hospital_display = ft.TextField(
            label="FHIR Server (Fixed)",
            value=DEFAULT_HOSPITAL_NAME,
            read_only=True,
            border=ft.InputBorder.NONE
        )

        status_text = ft.Text()

        def save_button_click(e):
            current_patient_id = session_patient_id
            status_text.value = "Fetching data..."
            status_text.color = ft.Colors.BLUE
            save_button.disabled = True
            page.update()

            url = DEFAULT_HOSPITAL_URL

            try:
                patient = fhir_utils.get_patient_data(int(current_patient_id), url)

                if patient is None:
                    status_text.value = f"Error: Could not find patient with ID {current_patient_id} at {DEFAULT_HOSPITAL_NAME}."
                    status_text.color = ft.Colors.RED
                    save_button.disabled = False
                    page.update()
                    return

                patient_data = fhir_utils.get_patient_data_dict(patient)

                page.client_storage.set(NAME_KEY, patient_data["name"])
                dob_iso = patient_data["date_of_birth"].isoformat() if patient_data.get("date_of_birth") else "N/A"
                page.client_storage.set(DOB_KEY, dob_iso)
                page.client_storage.set(GENDER_KEY, patient_data["gender"])
                page.client_storage.set(CONFIG_DONE_KEY, True)

                print(f"Data for patient '{patient_data['name']}' (ID: {current_patient_id}) fetched!")
                page.go("/main")

            except Exception as ex:
                print(f"Error fetching or saving patient data: {ex}")
                status_text.value = f"Error: An unexpected error occurred. Check console log."
                status_text.color = ft.Colors.RED
                save_button.disabled = False
                page.update()

        save_button = ft.ElevatedButton(
            text="Fetch & Save Data",
            on_click=save_button_click,
            icon=ft.Icons.CLOUD_DOWNLOAD
        )

        note_color = ft.colors.with_opacity(0.7, ft.Colors.ON_SURFACE)

        return [
            ft.Text("Configure Data Source", size=24, weight=ft.FontWeight.BOLD),
            ft.Text(f"Fetching data for Patient ID: {session_patient_id}."),
            hospital_display,
            ft.Text(
                "*Your medical data will be stored locally for this session.",
                italic=True, size=12, color=note_color
            ),
            save_button,
            status_text,
            ft.Container(height=20),
            # Cancel button is functionally removed now as config is always initial
            ft.Container() # Empty container where Cancel button was
        ]


    # --- View Building Functions ---

    def build_login_view():
        """Builds the Patient Selection View."""

        def handle_patient_selection(selected_id):
            """Stores selected ID and navigates to config."""
            print(f"Patient selected. ID: {selected_id}")
            page.client_storage.set(SESSION_PATIENT_ID_KEY, selected_id)
            page.go("/config/initial")

        patient_tiles = []
        for name, patient_id in USER_PATIENT_IDS.items():
            current_id = patient_id
            tile = ft.ListTile(
                leading=ft.Icon(ft.Icons.PERSON_OUTLINE),
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
                scroll=ft.ScrollMode.ADAPTIVE,
            )

        return ft.View(
            "/login",
            [
                ft.AppBar(title=ft.Text("Log in"), bgcolor=ft.Colors.SURFACE_TINT),
                ft.Column(
                    [
                        ft.Text("Select your account to continue:", size=16, weight=ft.FontWeight.W_500),
                        ft.Divider(height=20),
                        patient_content,
                    ],
                    expand=True,
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=15,
                )
            ],
            padding=ft.padding.all(20),
            vertical_alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )


    def build_config_view(is_initial_setup=False):
        """Builds the Configuration View."""
        route = "/config/initial"
        title = "Initial Configuration"

        return ft.View(
            route,
            [
                ft.AppBar(title=ft.Text(title), bgcolor=ft.Colors.SURFACE_TINT, automatically_imply_leading=False),
                ft.Column(
                    build_config_page_content(is_initial_setup=True),
                    expand=True,
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    scroll=ft.ScrollMode.ADAPTIVE
                )
            ],
            vertical_alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            padding=ft.padding.all(20)
        )

    def build_main_app_view():
        """Builds the main application View with NavigationBar."""

        main_content_area = ft.Container(
            content=None,
            expand=True,
            alignment=ft.alignment.center,
            padding=ft.padding.all(20)
        )

        def on_navigation_change(e):
            selected_index = e.control.selected_index
            content_column = None
            if selected_index == 0:
                content_column = ft.Column(
                    build_services_page_content(),
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=10
                )
            elif selected_index == 1:
                 content_column = ft.Column(
                    build_my_data_page_content(),
                     horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                     alignment=ft.MainAxisAlignment.START
                 )
            elif selected_index == 2:
                 session_patient_id = page.client_storage.get(SESSION_PATIENT_ID_KEY) or "Unknown"
                 content_column = ft.Column(
                    [
                        ft.Text("Configuration", size=24, weight=ft.FontWeight.BOLD),
                        ft.Text(f"Re-fetch data for current session (Patient ID: {session_patient_id})."),
                        ft.ElevatedButton("Re-fetch Data", on_click=lambda _: page.go("/config/initial"), icon=ft.Icons.REFRESH)
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=10
                )
            main_content_area.content = content_column
            main_content_area.update()

        initial_content_column = ft.Column(
             build_my_data_page_content(),
             horizontal_alignment=ft.CrossAxisAlignment.CENTER,
             alignment=ft.MainAxisAlignment.START
         )
        main_content_area.content = initial_content_column

        return ft.View(
            "/main",
            [
                 main_content_area
            ],
            appbar=ft.AppBar(
                title=ft.Text("External Medical Service"),
                bgcolor=ft.Colors.SURFACE_TINT,
                actions=[
                    ft.IconButton(
                        icon=ft.Icons.LOGOUT,
                        tooltip="Logout (Select New Patient)",
                        on_click=lambda _: page.go("/login")
                    )
                ]
            ),
            navigation_bar=ft.NavigationBar(
                destinations=[
                    ft.NavigationBarDestination(icon=ft.Icons.MEDICAL_SERVICES_OUTLINED, selected_icon=ft.Icons.MEDICAL_SERVICES, label="Service"),
                    ft.NavigationBarDestination(icon=ft.Icons.PERSON_OUTLINE, selected_icon=ft.Icons.PERSON, label="My Data"),
                    ft.NavigationBarDestination(icon=ft.Icons.SETTINGS_OUTLINED, selected_icon=ft.Icons.SETTINGS, label="Configuration"),
                ],
                selected_index=1,
                on_change=on_navigation_change,
            ),
        )

    def route_change(route):
        """Handles navigation between different application views."""
        print(f"Route changed to: {page.route}")
        page.views.clear()

        if page.route == "/login" or page.route == "/" or page.route == "":
            page.views.append(build_login_view())
        elif page.route == "/config/initial":
            if not page.client_storage.contains_key(SESSION_PATIENT_ID_KEY):
                 print("Error: Tried to access config without selecting a patient. Redirecting to login.")
                 page.go("/login")
                 return
            page.views.append(build_config_view(is_initial_setup=True))
        elif page.route == "/main":
            if not page.client_storage.get(CONFIG_DONE_KEY) or not page.client_storage.contains_key(SESSION_PATIENT_ID_KEY):
                 print("Config not done or patient not selected. Redirecting to login.")
                 page.go("/login")
                 return
            else:
                 page.views.append(build_main_app_view())
        else:
             print(f"Unknown route: {page.route}. Redirecting to login.")
             page.go("/login")
             return
        page.update()

    def view_pop(view):
        """Handles back navigation."""
        current_route = page.route
        if len(page.views) > 1:
            previous_route = page.views[-2].route
            if current_route == "/config/initial" and previous_route == "/login":
                 print("Preventing back navigation from initial config to login.")
                 return
            page.views.pop()
            top_view = page.views[-1]
            page.go(top_view.route)


    page.on_route_change = route_change
    page.on_view_pop = view_pop

    print("App starting, navigating to /login.")
    page.go("/login")

ft.app(target=main)
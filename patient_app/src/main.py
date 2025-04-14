import flet as ft
import fhir_utils

def main(page: ft.Page):
    page.adaptive = True
    page.title = "External Medical Service"

    page.appbar = ft.AppBar(
        title=ft.Text("External Medical Service"),
        bgcolor=ft.Colors.with_opacity(0.04, ft.CupertinoColors.SYSTEM_BACKGROUND),
    )

    STORAGE_PREFIX = "agedap.medical."

    def services_page():
        return [ 
            ft.Text("Services")
        ]
    
    def my_data_page():
        def load_body():
            if not page.client_storage.contains_key(f"{STORAGE_PREFIX}name"):
                return ft.Text("For downloading your data first configure your Hospital and Patient ID")
            else:
                print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
                print(page.client_storage.get(f"{STORAGE_PREFIX}date_of_birth"))
                return ft.Column(
                    [
                        ft.Row([
                            ft.Text("Name:"), 
                            ft.TextField(value=page.client_storage.get(f"{STORAGE_PREFIX}name"), read_only=True)
                        ]),
                        ft.Row([
                            ft.Text("Date of Birth:"), 
                            ft.TextField(value=page.client_storage.get(f"{STORAGE_PREFIX}date_of_birth"), read_only=True)
                        ]),
                        ft.Row([
                            ft.Text("Gender:"), 
                            ft.TextField(value=page.client_storage.get(f"{STORAGE_PREFIX}gender"), read_only=True)
                        ]),
                    ]
                )

        return [
            ft.Text("My Data"),
            load_body()
        ]
    
    def config_page():
        patient_id_field = ft.TextField(hint_text="e.g. 792264", value="792264")
        hospital_dropdown = ft.Dropdown(
            width=200,
            options=[
                ft.dropdown.Option("HAPI Sandbox"),
                ft.dropdown.Option("Other")
            ]
        )
        single_use_key_field = ft.TextField(hint_text="Type here...")

        def save_button_click(e):
            url = None
            if(hospital_dropdown.value == "HAPI Sandbox"):
                url = 'https://hapi.fhir.org/baseR5'

            patient = fhir_utils.get_patient_data(int(patient_id_field.value), url)

            # Store patient data in client storage
            patient_data = fhir_utils.get_patient_data_dict(patient)
            page.client_storage.set(f"{STORAGE_PREFIX}name", patient_data["name"])
            page.client_storage.set(f"{STORAGE_PREFIX}date_of_birth", patient_data["date_of_birth"].isoformat())
            page.client_storage.set(f"{STORAGE_PREFIX}gender", patient_data["gender"])

        return [
            ft.Text("Single Use Key:"),
            single_use_key_field,
            ft.Text("Your hospital:"),
            hospital_dropdown,
            ft.Text("Patient ID:"),
            patient_id_field,
            ft.Text("*Your medical data will be stored locally and wont be shared without previous encryption"),
            ft.ElevatedButton(text="Save", on_click=save_button_click)
        ]

    # Rest of your code remains the same
    content = ft.Column()

    for elem in my_data_page():
        content.controls.append(elem)

    def on_navigation_change(e):
        content.controls.clear()
        if e.control.selected_index == 0:
            for elem in services_page():
                content.controls.append(elem)
        elif e.control.selected_index == 1:
            for elem in my_data_page():
                content.controls.append(elem)
        elif e.control.selected_index == 2:
            for elem in config_page():
                content.controls.append(elem)
        content.update()

    page.navigation_bar = ft.NavigationBar(
        destinations=[
            ft.NavigationBarDestination(icon=ft.Icons.BUSINESS, label="Service"),
            ft.NavigationBarDestination(icon=ft.Icons.PERSON, label="My Data"),
            ft.NavigationBarDestination(icon=ft.Icons.SETTINGS, label="Configuration"),
        ],
        selected_index=1,
        on_change=on_navigation_change,
        border=ft.Border(
            top=ft.BorderSide(color=ft.CupertinoColors.SYSTEM_GREY2, width=0)
        ),
    )

    page.add(
        ft.SafeArea(
            ft.Column(
                [content],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            )
        )
    )

ft.app(main)

import flet as ft
import fhir_utils

def main(page: ft.Page):
    page.adaptive = True
    page.title = "External Medical Service"

    page.appbar = ft.AppBar(
        title=ft.Text("External Medical Service"),
        bgcolor=ft.Colors.with_opacity(0.04, ft.CupertinoColors.SYSTEM_BACKGROUND),
    )

    def services_page():
        return [ 
            ft.Text("Services")
            # meter que solo se ponga en enabled el botón si hay una clave guardada en config
        ]
    
    def my_data_page():
        return [
            ft.Text("My Data")
            # meter que solo se descarguen los datos si hay un link rollo lo del apirest del anterior en config (hacer el paripe con el anterior)
        ]
    
    def config_page():
        patient_id_field = ft.TextField(hint_text="e.g. 80219")
        hospital_dropdown = ft.Dropdown(
            width=200,
            options=[
            ft.dropdown.Option("HAPI Sandbox"),
            ft.dropdown.Option("Other")
            ]
        )
        single_use_key_field = ft.TextField(hint_text="Type here...")

        def save_button_click(e):
            print(patient_id_field.value)
            url = None
            if(hospital_dropdown.value == "HAPI Sandbox"):
                url = 'https://hapi.fhir.org/baseR5'

            retreived_patient = fhir_utils.get_patient_data(int(patient_id_field.value), url)

            # TODO use db_utils.save_patient() when OMOPCMD is configured
            # temporally using direct variables

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

    content = ft.Column()

    for elem in config_page():
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
        selected_index=2,
        on_change=on_navigation_change,
        border=ft.Border(
            top=ft.BorderSide(color=ft.CupertinoColors.SYSTEM_GREY2, width=0)
        ),
    )

    page.add(
        ft.SafeArea(
            ft.Column(
                [
                    content,
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            )
        )
    )

ft.app(main)

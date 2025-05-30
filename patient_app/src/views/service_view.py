import flet as ft
from api_client.base_client import BaseClient
from app_config import SERVICE_CONFIGS
import omop_utils 

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

        prediction_result_text = ft.Text("")

        def run_prediction_on_click(e):
            try:
                prediction_result_text.value = "Processing: Fetching OMOP data and running prediction..."
                page.update()

                scheme = client.request_info()
                omop_data = omop_utils.get_data(scheme) 
                
                prediction = client.request_prediction(omop_data)
                print(f"Prediction result: {prediction}")
                if prediction: 
                    prediction_result_text.value = (
                        "Preliminary Assessment:\n"
                        "This tool has identified some patterns that your doctor might want to review with you. "
                        "We encourage you to schedule a consultation."
                    )
                else:
                    prediction_result_text.value = (
                        "Preliminary Assessment:\n"
                        "The results of this assessment are favorable, you are most likely not at risk. "
                        "This tool is not a substitute for full professional medical advice, "
                        "and it is recommended to continue regular check-ups with your healthcare provider."
                    )
            except AttributeError as ae:
                prediction_result_text.value = f"Error: A required method might be missing. {ae}"
            except ImportError:
                prediction_result_text.value = "Error: Failed to use omop_utils. Import issue?"
            except Exception as ex:
                prediction_result_text.value = f"Error during prediction: {str(ex)}"
            page.update()

        predict_button = ft.ElevatedButton(
            "Run Service", 
            on_click=run_prediction_on_click
        )
        
        content_controls.extend([predict_button, prediction_result_text])

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
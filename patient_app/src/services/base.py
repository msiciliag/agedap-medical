class AIService:
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description

    def run(self, patient_data: dict) -> dict:
        raise NotImplementedError("Each service must implement the run method.")

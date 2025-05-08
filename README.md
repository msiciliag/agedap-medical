# Agedap Medical PPML (Proof of Concept)

This proof of concept (PoC) explores a platform for medical applications, featuring a patient-facing application and backend provider services. The services implemented are based on Privacy Preserving Machine Learning models from the ConcreteML library, demonstrating the potential of FHE (Fully Homomorphic Encryption) in healthcare.

## Quick Start

Refer to README.md files inside `/patient_app` and `/provider` for a quick setup of each part of the project. 
> [!TIP]
> Start with `/provider/README.md`.

## Project Structure

The project is organized into two main components:

*   **`/patient_app`**: This directory contains the source code for the patient application. It allows patients to interact with their data and various medical services in a simulated environment.
*   **`/provider`**: This directory contains the backend services that the patient application consumes. These services showcase AI models for predictions and data processing.

## Overview

The Agedap Medical PoC aims to demonstrate the feasibility of integrating a user-friendly application with backend Privacy Preserving Machine Learning medical services. 

> [!NOTE]  
> This project serves as an initial exploration, it is not a production-ready solution.

### Patient Application (`patient_app`)

The patient application provides a conceptual interface for patients to:
*   Access simulated medical information using HL7 FHIR interoperability standard.
*   Utilize available and private medical services (e.g., screenings, classifications) for demonstration purposes.
*   Manage mock health data based on OMOP CMD.

### Provider Services (`provider`)

The provider services offer example functionalities, which include:
*   FHE machine learning models for tasks like breast cancer screening and diabetes classification, intended for evaluation.
*   APIs for data exchange and communication with the patient application.
*   Training scripts and configurations for the ML models, provided for experimentation.

## Contributing

As a proof of concept, contributions are currently focused on exploring and validating the core ideas. If you have suggestions, bug reports, or would like to discuss potential enhancements related to the PoC's objectives, please feel free to open an issue.

## License

License information will be specified at a later date.

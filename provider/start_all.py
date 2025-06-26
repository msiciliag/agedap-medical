import os
import subprocess
import time
import sys
import logging

logger = logging.getLogger(__name__)
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
provider_dir = os.path.join(project_root, "provider")
if provider_dir not in sys.path:
    sys.path.insert(0, provider_dir)

try:
    from train import train_and_save, load_config
except ImportError:
    logger.error(f"Error: Could not import 'train_and_save' and 'load_config' from 'provider.train'. Ensure 'provider/train.py' exists and '{provider_dir}' is in PYTHONPATH.")
    sys.exit(1)

def check_model_exists(directory_path):
    """
    Checks if the FHE model directory exists and contains essential files.
    A simple check for 'server.zip' which is created by FHEModelDev.save().
    """
    if not os.path.isabs(directory_path):
        abs_directory_path = os.path.join(project_root, directory_path)
    else:
        abs_directory_path = directory_path
    
    server_zip_path = os.path.join(abs_directory_path, "server.zip")
    return os.path.isfile(server_zip_path)

def start_flask_server(server_script_path_relative, port, service_name):
    """Starts a Flask server as a background process."""
    absolute_script_path = os.path.join(project_root, server_script_path_relative)

    if not os.path.exists(absolute_script_path):
        logger.error(f"Error: Server script not found at {absolute_script_path} for {service_name}")
        return None

    logger.info(f"Starting {service_name} server ({server_script_path_relative}) on port {port}...")
    
    safe_service_name = "".join(c if c.isalnum() else "_" for c in service_name)
    log_file_stdout = os.path.join(project_root, f"{safe_service_name}_stdout.log")
    log_file_stderr = os.path.join(project_root, f"{safe_service_name}_stderr.log")

    try:
        with open(log_file_stdout, 'wb') as out_log, open(log_file_stderr, 'wb') as err_log:
            process = subprocess.Popen(
                [sys.executable, absolute_script_path], 
                stdout=out_log,
                stderr=err_log,
                cwd=os.path.dirname(absolute_script_path) 
            )
        logger.info(f"{service_name} server starting with PID {process.pid}. Logs: {log_file_stdout}, {log_file_stderr}")
        return process
    except Exception as e:
        logger.error(f"Error starting {service_name} server: {e}")
        return None

def main():
    config_file_path_relative = os.path.join("provider", "training_config.yaml")
    config_path_absolute = os.path.join(project_root, config_file_path_relative)

    if not os.path.exists(config_path_absolute):
        logger.error(f"Error: Configuration file not found at {config_path_absolute}")
        return

    config = load_config(config_path_absolute)
    running_servers_pids = []

    for service_config in config.get("datasets", []):
        service_name = service_config.get("service_name", f"DatasetID_{service_config.get('dataset_id')}")
        output_dir_config = service_config.get("output_directory")
        dataset_id = service_config.get("dataset_id")
        n_estimators = service_config.get("n_estimators", 10)
        max_depth = service_config.get("max_depth", 5)
        server_script_relative = service_config.get("server_script")
        server_port = service_config.get("server_port")

        if not all([output_dir_config, dataset_id is not None, server_script_relative, server_port is not None]):
            logger.warning(f"Skipping service '{service_name}' due to incomplete configuration (missing output_directory, dataset_id, server_script, or server_port).")
            continue

        logger.info(f"\nProcessing service: {service_name}")

        if os.path.isabs(output_dir_config):
            output_dir_absolute = output_dir_config
        else:
            output_dir_absolute = os.path.join(project_root, output_dir_config)
        
        os.makedirs(os.path.dirname(output_dir_absolute), exist_ok=True)


        if not check_model_exists(output_dir_absolute):
            logger.info(f"Model for '{service_name}' not found in '{output_dir_absolute}'. Training model...")
            try:
                train_and_save(
                    dataset_id=dataset_id,
                    output_directory=output_dir_absolute,
                    n_estimators=n_estimators,
                    max_depth=max_depth
                )
                logger.info(f"Model for '{service_name}' trained and saved to '{output_dir_absolute}'.")
            except Exception as e:
                logger.error(f"Error training model for '{service_name}': {e}")
                logger.error(f"Skipping server start for '{service_name}' due to training error.")
                continue
        else:
            logger.info(f"Model for '{service_name}' already exists in '{output_dir_absolute}'.")

        server_process = start_flask_server(server_script_relative, server_port, service_name)
        if server_process:
            running_servers_pids.append(server_process.pid)
            time.sleep(2)

    if not running_servers_pids:
        logger.info("\nNo servers were started.")
    else:
        logger.info(f"\n{len(running_servers_pids)} services initiated. They are running in the background.")
        logger.info("Server PIDs:", running_servers_pids)
        logger.info("You can monitor their logs in the respective *_stdout.log and *_stderr.log files in the project root.")
        logger.info("To stop the servers, you'll need to manually terminate their processes (e.g., using 'kill <PID>').")

if __name__ == "__main__":
    main()
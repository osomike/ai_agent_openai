import requests
import time

from utils.logger import Logger

class DatabricksTool:
    def __init__(self, config: dict, logger: Logger = None):
        self.cluster_id = config["databricks"]["cluster_id"]
        self.workspace_url = config["databricks"]["workspace_url"]
        self.token = config["databricks"]["token"]

        if logger:
            self.logger = logger
        else:
            self.logger = Logger(logger_name="Databricks Tool")

        self.logger.info("Initializing Databricks Tool")

    def trigger_notebook(self, notebook_path: str, parameters: dict = None) -> dict:
        """
        Triggers a Databricks notebook job.

        Args:
            notebook_path (str): The path to the notebook to trigger.
            parameters (dict, optional): Parameters to pass to the notebook.

        Returns:
            dict: Response containing the job run ID or an error message.
        """
        if parameters is None:
            parameters = {}
        url = f"{self.workspace_url}/api/2.1/jobs/runs/submit"
        headers = {"Authorization": f"Bearer {self.token}"}
        payload = {
            "run_name": "AI Agent | Triggered via API",
            "existing_cluster_id": self.cluster_id,
            "notebook_task": {
                "notebook_path": notebook_path,
                "base_parameters": parameters
            }
        }

        self.logger.info(f"Triggering notebook: {notebook_path}")
        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            run_id = response.json().get("run_id")
            self.logger.info(f"Notebook triggered successfully. Run ID: {run_id}")
            return {"status": "success", "run_id": run_id}
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Failed to trigger notebook: {e}")
            return {"status": "error", "message": str(e)}

    def check_run_status(self, run_id: int) -> dict:
        """
        Checks the status of a Databricks notebook run.

        Args:
            run_id (int): The ID of the notebook run.

        Returns:
            dict: Response containing the run status or an error message.
        """
        url = f"{self.workspace_url}/api/2.1/jobs/runs/get"
        headers = {"Authorization": f"Bearer {self.token}"}
        params = {"run_id": run_id}

        self.logger.info(f"Checking status for run ID: {run_id}")
        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            #print(response.json())
            state = response.json().get("state", {})
            self.logger.info(f"Run status: {state}")
            return {"status": "success", "state": state}
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Failed to check run status: {e}")
            return {"status": "error", "message": str(e)}

    def check_run_output(self, run_id: int) -> dict:
        """
        Retrieves the output of a Databricks notebook run.

        Args:
            run_id (int): The ID of the notebook run.

        Returns:
            dict: Response containing the notebook output or an error message.
        """
        url = f"{self.workspace_url}/api/2.1/jobs/runs/get-output"
        headers = {"Authorization": f"Bearer {self.token}"}
        params = {"run_id": run_id}

        self.logger.info(f"Retrieving output for run ID: {run_id}")
        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            output = response.json().get("notebook_output", {})
            self.logger.info(f"Run output retrieved successfully.")
            return {"status": "success", "output": output}
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Failed to retrieve run output: {e}")
            return {"status": "error", "message": str(e)}


    def run_databricks_job(self, notebook_path: str, parameters: dict = None) -> dict:

        if notebook_path in [None, ""]:
            notebook_path = "/Workspace/Users/oscar.claure@digital-power.com/test"
            parameters = {
                "param1": "I am an AI agent",
            }

        response = self.trigger_notebook(
            notebook_path=notebook_path,
            parameters=parameters
        )

        run_id = response["run_id"]
        state = "RUNNING"
        sleep_time = 5

        while state == "RUNNING":
            self.logger.info(f"Job still in process, sleeping for {sleep_time} seconds...")
            time.sleep(sleep_time)    
            response = self.check_run_status(run_id=run_id)
            state = response["state"]["life_cycle_state"]
            self.logger.info(f"Run ID: {run_id} has state: '{state}'")

        self.logger.info(f"The job is completed, checking its return.")
        response = self.check_run_output(run_id=run_id)
        self.logger.info(f"Run ID: {run_id} has output: '{response}'")
        return response
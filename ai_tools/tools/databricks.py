from typing import Optional
import logging

import time
import requests

from utils.logger import Logger
from ai_tools.tools.tools_abstract import AIToolsAbstract

class DatabricksTool(AIToolsAbstract):

    def __init__(self, config: dict, logger: Optional[Logger] = None, log_level: int = logging.INFO):

        super().__init__()
        self.cluster_id = config["databricks"]["cluster_id"]
        self.workspace_url = config["databricks"]["workspace_url"]
        self.token = config["databricks"]["token"]

        if logger:
            self.logger = logger
        else:
            self.logger = Logger(logger_name="Databricks Tool", log_level=log_level)

        self.logger.info("Initializing Databricks Tool")
        self._tools = {
            "run_databricks_job": self.run_databricks_job,
        }
        self._tools_description = [
            {
                "type": "function",
                "function": {
                    "name": "run_databricks_job",
                    "description":
                        "Trigger a job inside databricks",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "notebook_path": {
                                "type": "string",
                                "description":
                                    "(Optional) The path of the notebook to trigger. If no path is specified, " \
                                    "the default path will be used."
                            },
                            "parameters": {
                                "type": "object",
                                "description":
                                    "(Optional) A dictionary of parameters to pass to the notebook. Defaults to None.",
                                "additionalProperties": True
                            },
                        #"required": ["notebook_path"]
                        }
                    }
                }
            }
        ]

    def trigger_notebook(self, notebook_path: str, parameters: Optional[dict] = None) -> dict:
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
            response = requests.post(url, headers=headers, json=payload, timeout=200)
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
            response = requests.get(url, headers=headers, params=params, timeout=200)
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
            response = requests.get(url, headers=headers, params=params, timeout=200)
            response.raise_for_status()
            output = response.json().get("notebook_output", {})
            self.logger.info(f"Run output for run '{run_id}' retrieved successfully.")
            return {"status": "success", "output": output}
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Failed to retrieve run output: {e}")
            return {"status": "error", "message": str(e)}


    def run_databricks_job(self, notebook_path: str, parameters: Optional[dict] = None) -> dict:
        """
        Executes a Databricks notebook job and monitors its status until completion.

        Args:
            notebook_path (str): The path to the Databricks notebook to execute. If None or an empty string is provided,
                a default notebook path will be used.
            parameters (dict, optional): A dictionary of parameters to pass to the notebook. Defaults to None.

        Returns:
            dict: The output of the completed Databricks job, including its results and status.
        """

        if parameters in [None, "", "{}"]:
            parameters = {
                "param1": "I am an AI agent",
            }

        if notebook_path in [None, "", "{}"]:
            notebook_path = "/Workspace/Users/oscar.claure@digital-power.com/test"

        response = self.trigger_notebook(
            notebook_path=notebook_path,
            parameters=parameters
        )

        run_id = response["run_id"]
        state = "RUNNING"
        sleep_time = 5

        while state in ["PENDING", "RUNNING"]:
            self.logger.info(f"Job still in process, sleeping for {sleep_time} seconds...")
            time.sleep(sleep_time)
            response = self.check_run_status(run_id=run_id)
            state = response["state"]["life_cycle_state"]
            self.logger.info(f"Run ID: {run_id} has state: '{state}'")

        self.logger.info(f'Response from is: {response}')
        if response["state"]["result_state"] in ["FAILED", "CANCELED"]:
            self.logger.error(f"Job failed with error: {response['state']['state_message']}")
            job_output = {"status": "error", "message": response["state"]["state_message"]}
        elif response["state"]["result_state"] == "SUCCESS":
            self.logger.info("The job is completed successfully, checking its return.")
            job_output = self.check_run_output(run_id=run_id)
            self.logger.info(f"Run ID: {run_id} has output: '{job_output}' from the notebook.")
        else:
            self.logger.error(f"Unknown result state: {response['state']['state_message']}")
            job_output = {"status": "error", "message": response["state"]["state_message"]}
        return job_output

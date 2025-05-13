import os

from utils.logger import Logger
from ai_tools.tools.databricks import DatabricksTool

class XPASurveyTool(DatabricksTool):

    def __init__(self, config: dict, logger: Logger = None):

        super().__init__(config=config, logger=logger)
        self.logger.info("Initializing Databricks Tool")
        self._tools = {
            "run_ingestion_job": self.run_ingestion_job,
        }
        self._tools_description = [
            {
                "type": "function",
                "function": {
                    "name": "run_ingestion_job",
                    "description":
                        "Trigger the ingestion job inside databricks, for survey data ingestion.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "path_to_input_file": {
                                "type": "string",
                                "description":
                                    "The file path pointint to the file containing the survey data"
                            },
                            "format_file": {
                                "type": "string",
                                "description":
                                    "(Optional) The format of the input file. Defaults to 'xlsx' for excel files."
                            },
                            "sheet_name": {
                                "type": "string",
                                "description":
                                    "(Optional) The name of the sheet to read from the input file, if input file " \
                                    "format is 'xlsx'. Defaults to 'Export'.",
                            },
                        },
                        "required": ["path_to_input_file"]
                    }
                }
            }
        ]

    def run_ingestion_job(self, path_to_input_file: str, format_file: str = "xlsx", sheet_name: str = "Export") -> dict:

        if format_file in [None, "", "{}"]:
            format_file = "xlsx"
        if sheet_name in [None, "", "{}"]:
            sheet_name = "Export"
        if format_file not in ["xlsx", "csv"]:
            message = f"Invalid file format: {format_file}. Supported formats are 'xlsx' and 'csv'."
            self.logger.error(message)
            return {"status": "error", "message": message}

        path_to_input_file = os.path.join("/mnt/dls/", path_to_input_file)
        self.logger.info(
            f"Running ingestion job with input file: {path_to_input_file}, format: {format_file}, sheet: {sheet_name}")

        notebook_path = \
            "/Workspace/Users/oscar.claure@digital-power.com/xpa-ai-agent-poc/survey_agent/data_ingestion"

        parameters = {
            "file_path": path_to_input_file,
            "file_format": format_file,
            "sheet_name": sheet_name
        }

        output = self.run_databricks_job(
            notebook_path=notebook_path,
            parameters=parameters
        )

        return output

    def run_creation_of_categories_job(self,
            number_of_categories: int,
            sample_fraction: float,
            question_id: str,
            study_id: str,
            survey_id : str,
            language: str = "English") -> dict:

        notebook_path = \
            "/Workspace/Users/oscar.claure@digital-power.com/xpa-ai-agent-poc/survey_agent/creation_of_categories"
        parameters = {
            "number_of_categories": number_of_categories,
            "sample_fraction": sample_fraction,
            "question_id": question_id,
            "study_id": study_id,
            "survey_id": survey_id,
            "language": language
        }

        output = self.run_databricks_job(
            notebook_path=notebook_path,
            parameters=parameters
        )

        return output

    def run_categorization_job(self, notebook_path: str = None, parameters: dict = None) -> dict:
        self.run_databricks_job(
            notebook_path=notebook_path,
            parameters=parameters
        )

    def run_ai_judge_job(self, notebook_path: str = None, parameters: dict = None) -> dict:
        self.run_databricks_job(
            notebook_path=notebook_path,
            parameters=parameters
        )

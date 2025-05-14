import os

from utils.logger import Logger
from ai_tools.tools.databricks import DatabricksTool

class XPASurveyTool(DatabricksTool):

    def __init__(self, config: dict, logger: Logger = None):

        super().__init__(config=config, logger=logger)
        self.logger.info("Initializing Databricks Tool")
        self._tools = {
            "run_ingestion_job": self.run_ingestion_job,
            "run_creation_of_categories_job": self.run_creation_of_categories_job,
        }
        self._tools_description = [
            {
                "type": "function",
                "function": {
                    "name": "run_ingestion_job",
                    "description":
                        "Trigger the ingestion job inside databricks, for survey data ingestion. This job will " \
                        "ingest the survey data from the input file. The job will take the file path, the file " \
                        "format and the sheet name as input parameters. The file format can be 'xlsx' or 'csv'. " \
                        "The sheet name is only required if the file format is 'xlsx'. The job will create a table " \
                        "that will be saved in unity catalog inside databricks.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "path_to_input_file": {
                                "type": "string",
                                "description":
                                    "The file path pointint to the file containing the survey data."
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
            },
            {
                "type": "function",
                "function": {
                    "name": "run_creation_of_categories_job",
                    "description":
                        "Trigger the creation of categories job in databricks, for survey open answers from " \
                        "survey data. This job will create categories for the open answers in the survey data. " \
                        "The categories will be created using the AI model. The job will take the " \
                        "number of categories to create, the sample fraction of the open answers to use to create " \
                        "the categories, the question id, the study id, the survey id and the language on which the " \
                        "answers are written as input parameters. A study id can contain multiple surveys and the " \
                        "surveys can contain multiple questions.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "number_of_categories": {
                                "type": "string",
                                "description":
                                    "The number of categories to create for the open answers."
                            },
                            "sample_fraction": {
                                "type": "string",
                                "description":
                                    "The sample fraction of the open answers to use to create the categories."
                            },
                            "question_id": {
                                "type": "string",
                                "description":
                                    "The question id of the open answers to create the categories for.",
                            },
                            "survey_id": {
                                "type": "string",
                                "description":
                                    "The survey id containing the open answers to create the categories for.",
                            },
                            "study_id": {
                                "type": "string",
                                "description":
                                    "The study id containing the survey data.",
                            },
                            "language": {
                                "type": "string",
                                "description":
                                    "(Optional) The language of the open answers. Defaults to 'English'.",
                            },
                        },
                        "required": ["number_of_categories", "sample_fraction", "question_id",
                                    "survey_id", "study_id"]
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

        number_of_categories = int(number_of_categories)
        sample_fraction = float(sample_fraction)
        if language in [None, "", "{}"]:
            language = "English"
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

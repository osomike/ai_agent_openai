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
                            "study_id": {
                                "type": "string",
                                "description":
                                    "The study id containing the survey data.",
                            },
                            "survey_id": {
                                "type": "string",
                                "description":
                                    "The survey id containing the open answers to create the categories for.",
                            },
                            "question_id": {
                                "type": "string",
                                "description":
                                    "The question id of the open answers to create the categories for.",
                            },
                            "language": {
                                "type": "string",
                                "description":
                                    "(Optional) The language of the open answers. Defaults to 'English'.",
                            },
                        },
                        "required": ["number_of_categories", "sample_fraction", "study_id", "survey_id", "question_id"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "run_categorization_job",
                    "description":
                        "Trigger the categorization job in databricks, for survey open answers from " \
                        "survey data. This job will categorize the open answers in the survey data. The job will " \
                        "take the question id, the study id and the survey id as input parameters. A study id can " \
                        "contain multiple surveys and the surveys can contain multiple questions.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "study_id": {
                                "type": "string",
                                "description":
                                    "The study id containing the survey data.",
                            },
                            "survey_id": {
                                "type": "string",
                                "description":
                                    "The survey id containing the open answers to create the categories for.",
                            },
                            "question_id": {
                                "type": "string",
                                "description":
                                    "The question id of the open answers to create the categories for.",
                            }
                        },
                        "required": ["study_id", "survey_id", "question_id"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "run_ai_judge_job",
                    "description":
                        "Trigger the AI judge job in databricks, for survey open answers from " \
                        "survey data. This job will validate the results of the categorization job. The job will " \
                        "take the question id, the study id and the survey id as input parameters. A study id can " \
                        "contain multiple surveys and the surveys can contain multiple questions.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "study_id": {
                                "type": "string",
                                "description":
                                    "The study id containing the survey data.",
                            },
                            "survey_id": {
                                "type": "string",
                                "description":
                                    "The survey id containing the open answers to create the categories for.",
                            },
                            "question_id": {
                                "type": "string",
                                "description":
                                    "The question id of the open answers to create the categories for.",
                            }
                        },
                        "required": ["study_id", "survey_id", "question_id"]
                    }
                }
            }
        ]

    def run_ingestion_job(self, path_to_input_file: str, format_file: str = "xlsx", sheet_name: str = "Export") -> dict:
        """
        Executes an ingestion job to process a file and load its data.

        This method validates the input file format and sheet name, constructs the file path,
        and triggers a Databricks notebook job to handle the ingestion process.

        Args:
            path_to_input_file (str): The relative path to the input file to be ingested.
            format_file (str, optional): The format of the input file. Defaults to "xlsx".
                                         Supported formats are "xlsx" and "csv".
            sheet_name (str, optional): The name of the sheet to process in the input file.
                                        Defaults to "Export".

        Returns:
            dict: A dictionary containing the status and message of the ingestion job.
                  Example:
                  {
                      "status": "success" or "error",
                      "message": "Details about the job execution"
                    }
        """

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
            "/Workspace/Users/oscar.claure@digital-power.com/xpa-ai-agent-poc/" \
            "survey_agent/data_ingestion"

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
        """
        Executes a Databricks job to create categories for a survey question.

        Args:
            number_of_categories (int): The number of categories to create.
            sample_fraction (float): The fraction of the sample to use for category creation.
            question_id (str): The ID of the question for which categories are being created.
            study_id (str): The ID of the study associated with the survey.
            survey_id (str): The ID of the survey.
            language (str, optional): The language for the categories. Defaults to "English".

        Returns:
            dict: The output of the Databricks job execution.
        """
        number_of_categories = int(number_of_categories)
        sample_fraction = float(sample_fraction)
        if language in [None, "", "{}"]:
            language = "English"
        notebook_path = \
            "/Workspace/Users/oscar.claure@digital-power.com/xpa-ai-agent-poc/" \
            "survey_agent/creation_of_categories"
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

    def run_categorization_job(self, question_id: str, study_id: str, survey_id : str) -> dict:
        """
        Executes a categorization job on a Databricks notebook for a specific survey question. The catagorization
        job is designed to categorize open-ended survey responses into already predefined categories
        (check job run_creation_of_categories_job).

        Args:
            question_id (str): The unique identifier of the survey question to be categorized.
            study_id (str): The unique identifier of the study associated with the survey.
            survey_id (str): The unique identifier of the survey.

        Returns:
            dict: The output of the Databricks job execution, typically containing the results of the
            categorization process.
        """
        notebook_path = \
            "/Workspace/Users/oscar.claure@digital-power.com/xpa-ai-agent-poc/" \
            "survey_agent/classification_into_categories"
        parameters = {
            "question_id": question_id,
            "study_id": study_id,
            "survey_id": survey_id
            }

        output = self.run_databricks_job(
            notebook_path=notebook_path,
            parameters=parameters
        )

        return output

    def run_ai_judge_job(self, question_id: str, study_id: str, survey_id : str) -> dict:
        """
        Executes a Databricks job to validate results for a specific survey question using an AI judge.
        This method triggers a Databricks notebook job that performs validation on the survey question's
        categorization results.
        This method is typically used to ensure the quality and accuracy of the categorization process.
        The AI judge evaluates the categorization results and provides feedback or validation metrics.

        Args:
            question_id (str): The unique identifier of the question to be validated.
            study_id (str): The unique identifier of the study associated with the survey.
            survey_id (str): The unique identifier of the survey containing the question.

        Returns:
            dict: The output of the Databricks job execution, typically containing the results of 
            the validation process.
        """
        notebook_path = \
            "/Workspace/Users/oscar.claure@digital-power.com/xpa-ai-agent-poc/" \
            "survey_agent/ai_judge_validation"
        parameters = {
            "question_id": question_id,
            "study_id": study_id,
            "survey_id": survey_id
            }

        output = self.run_databricks_job(
            notebook_path=notebook_path,
            parameters=parameters
        )

        return output

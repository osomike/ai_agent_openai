# AI Agent OpenAI

This project provides an AI-powered assistant designed to help users manage survey data and file-related operations. The AI Agent leverages Azure OpenAI, Databricks, and Azure Blob Storage to perform various tasks efficiently.

## Features and Capabilities

### 1. **Azure Blob Storage Management**
   - **List Files**: Retrieve a list of files in a specified Azure Blob Storage container.
   - **Upload Files**: Upload files to Azure Blob Storage.
   - **Download Files**: Download files from Azure Blob Storage to a local directory.
   - **Delete Files**: Remove files from Azure Blob Storage.

### 2. **Local File Management**
   - **List Files**: List files in a specified local directory.
   - **Delete Files**: Delete files from the local file system.

### 3. **Databricks Job Management**
   - **Run Ingestion Jobs**: Ingest survey data from files (Excel or CSV) into Databricks.
   - **Create Categories**: Automatically generate categories for open-ended survey answers using AI.
   - **Categorize Responses**: Assign open-ended survey answers to predefined categories.
   - **AI Judge Validation**: Validate categorization results using an AI-powered judge.

### 4. **Interactive AI Assistant**
   - Engage in a conversation with the AI assistant to manage tasks.
   - Use natural language to trigger operations like file management or survey data processing.
   - The assistant can reason about whether one or multiple tool calls are needed to fulfill a request.

---

## Getting Started

### Prerequisites
1. **Python 3.13** or higher.
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Configure your Azure and Databricks credentials in `config/settings.yaml`.

Running the AI Agent
1. Start the AI Agent by running the `main.py` script:
   ```python
   python main.py
   ```
2. The agent will prompt you for input. You can ask it to perform tasks related to file management, survey data
processing or any other general inquiries.

## Usage

Commands
- Ask a Question: Type your query, and the assistant will respond.
- Exit the Conversation: Type `exit/` to quit.
- Reset the Conversation: Type `reset/` to clear the conversation history.
- Print Conversation History: Type `print/` to display the conversation history.
- View Raw Conversation Data: Type `conversation/` to see the raw JSON of the 

Example Interactions
1. List Files in Azure Blob Storage:
    ```
    Human User: List files in the dls Azure Blob Storage container.
    AI assitant: Here are the files in the container:
    - file1.csv
    - file2.xlsx
    ```
2. Upload a File to Azure Blob Storage:
    ```
    Human User: Upload the file report.csv to the Azure Blob Storage container.
    AI assistant: Uploading report.csv to the container...
    File uploaded successfully.
    ```
3. Run a Databricks Job:
    ```
    Human User: Run the ingestion job for the file survey_data.csv.
    AI assistant: Running the ingestion job...
    Job completed successfully.
    ```

## Configuration

`config/settings.yaml` contains the configuration for Azure Blob Storage, Databricks, and other tools. Update it with your credentials and settings.

```yaml
azure_openai:
    endpoint: "https://your-openai-resource-name.openai.azure.com/"
    model_name: "gpt-4"
    deployment: "gpt-4-deployment"
    api_key: "your-azure-openai-api-key"
    api_version: "2024-12-01-preview"

azure_blob:
    connection_string: "DefaultEndpointsProtocol=https;AccountName=youraccountname;AccountKey=youraccountkey;EndpointSuffix=core.windows.net"
    default_container: "dls"

local_storage:
    folder: "/Users/mike/Documents/local_storage"

databricks:
    workspace_url: "https://your-databricks-instance.cloud.databricks.com"
    token: "your-databricks-access-token"
    cluster_id: "your-cluster-id"
    notebooks_dir_path: "/Workspace/Notebooks"
    notebook_name: "data_ingestion_notebook"
```

`config/prompts.yaml` defines the system prompt and behavior of the AI assistant. You can customize it to suit your needs.

## Logging

Logs are generated using a custom `Logger` class, which supports configurable logging levels. You can specify the desired logging level (e.g., `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`) when running the `main.py` script using the `--log-level` parameter. Logs can be directed to the console, a file, or both, depending on your configuration.

Example:
```bash
python main.py --log-level DEBUG
```

This will set the logging level to `DEBUG`, providing detailed information about the application's execution.



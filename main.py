"""Main entry point for the AI Agent application."""

import logging
import argparse

from core.ai_agent import AIAgent

# Parse command-line arguments for log level
parser = argparse.ArgumentParser(description="AI Agent Application")
parser.add_argument(
    "--log-level",
    type=str,
    default="WARNING",
    choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
    help="Set the logging level (default: INFO)"
)
args = parser.parse_args()

# Set the logging level
log_level = getattr(logging, args.log_level.upper(), logging.INFO)

# Initialize the AI Agent
ai_agent = AIAgent(config_path="config/settings.yaml", prompt_path="config/prompts.yaml", log_level=log_level)
ai_agent.logger.info("AI Agent initialized successfully.")
ai_agent.start()

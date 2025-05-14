"""Main entry point for the AI Agent application."""

import logging
import argparse

from core.ai_agent import AIAgent

def get_parser():
    """
    Creates and returns an argument parser for the AI Agent Application.

    Returns:
        argparse.ArgumentParser: The configured argument parser.
    """
    # Parse command-line arguments for log level
    parser = argparse.ArgumentParser(description="AI Agent Application")
    parser.add_argument(
        "--log-level",
        type=str,
        default="WARNING",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Set the logging level (default: INFO)"
    )
    return parser

def main():
    """
    Main entry point for the AI Agent application.

    This function initializes the argument parser, sets the logging level, and starts the AI Agent.

    Steps:
    1. Parse command-line arguments using the argument parser.
    2. Set the logging level based on the provided argument or default to INFO.
    3. Initialize and Start the AI Agent.

    Dependencies:
    - Requires a valid configuration file at "config/settings.yaml".
    - Requires a valid prompt file at "config/prompts.yaml".
    """

    parser = get_parser()
    args = parser.parse_args()

    # Set the logging level
    log_level = getattr(logging, args.log_level.upper(), logging.INFO)

    # Initialize the AI Agent
    ai_agent = AIAgent(config_path="config/settings.yaml", prompt_path="config/prompts.yaml", log_level=log_level)
    ai_agent.logger.info("AI Agent initialized successfully.")
    ai_agent.start()

if __name__ == "__main__":
    main()

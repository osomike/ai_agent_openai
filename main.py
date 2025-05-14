"""Main entry point for the AI Agent application."""

from core.ai_agent import AIAgent

ai_agent = AIAgent(config_path="config/settings.yaml", prompt_path="config/prompts.yaml")
ai_agent.logger.info("AI Agent initialized successfully.")
ai_agent.start()


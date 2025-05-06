from core.ai_agent import AIAgent

ai_agent = AIAgent(config_path="config/settings.yaml")
ai_agent.logger.info("AI Agent initialized successfully.")
ai_agent.start()

import logging
from threading import Lock
from typing import Dict


class Config:
    _initialized = False
    _instance: "Config" = None
    _lock = Lock()
    logger: logging.Logger = None
    agent_loggers: Dict[int, logging.Logger] = {}

    def __new__(cls):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super(Config, cls).__new__(cls)
                    cls._instance._setup_logger()
                    cls._instance.agent_loggers = {}
                    cls._instance._initialized = True
        return cls._instance

    def _setup_logger(self):
        self.logger = logging.getLogger("ThreadSafeLogger")
        self.logger.setLevel(logging.DEBUG)

        console_handler = logging.StreamHandler()
        file_handler = logging.FileHandler("logs/app.log")

        console_handler.setLevel(logging.INFO)
        file_handler.setLevel(logging.DEBUG)

        formatter = logging.Formatter(
            "%(asctime)s - %(threadName)s - %(levelname)s - %(message)s - %(filename)s (%(lineno)d)"
        )
        console_handler.setFormatter(formatter)
        file_handler.setFormatter(formatter)

        if not self.logger.hasHandlers():
            self.logger.addHandler(console_handler)
            self.logger.addHandler(file_handler)

    def get_agent_logger(self, agent_id: int) -> logging.Logger:
        """
        Returns a logger for a specific agent. Creates one if it doesn't exist.
        """
        if agent_id not in self.agent_loggers:
            agent_logger = logging.getLogger(f"Agent_{agent_id}")
            agent_logger.setLevel(logging.DEBUG)

            # Create a file handler for the agent
            agent_file_handler = logging.FileHandler(f"logs/agent_{agent_id}.log")
            agent_file_handler.setLevel(logging.DEBUG)

            formatter = logging.Formatter(
                "%(asctime)s - %(threadName)s - %(levelname)s - %(message)s - %(filename)s (%(lineno)d)"
            )
            agent_file_handler.setFormatter(formatter)

            # Prevent adding multiple handlers if the logger already has handlers
            if not agent_logger.hasHandlers():
                agent_logger.addHandler(agent_file_handler)

            # Prevent the agent logger from propagating to the root logger
            agent_logger.propagate = False

            self.agent_loggers[agent_id] = agent_logger

        return self.agent_loggers[agent_id]

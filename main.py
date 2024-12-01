import threading
from typing import List

from shapely import Polygon

from agents.agent import Agent
from config import Config
from environment.main import Environment
from utils import write_positions_to_file


class Simulation:

    def __init__(self, number_agents: int, area: Polygon):
        self.config = Config()
        self.logger = self.config.logger

        self.number_agents = number_agents
        self.agents: List[Agent] = []
        self.area = area
        self.threads: List[threading.Thread] = []
        self.stop_event = threading.Event()

    def _start_environment(self):
        self.logger.info("Starting environment")
        self.environment = Environment(self.config, self.number_agents, self.area)
        self.logger.debug("Environment started")

    def _start_agents(self):
        self.logger.info("Starting agents")
        for i in range(self.number_agents):
            agent = Agent(i, i == 0, self.config, self.environment)
            self.agents.append(agent)
            initial_position = self.environment.area.centroid
            self.environment.set_position(i, initial_position)
            self.logger.debug(f"Agent {i} initialized at position {initial_position}")

    def run(self):
        self.logger.info("Simulation run started")
        self._start_environment()
        self._start_agents()
        for agent in self.agents:
            thread = threading.Thread(target=agent.run, name=f"Agent-Thread-{agent.id}")
            thread.start()
            self.threads.append(thread)
            self.logger.debug(f"Agent {agent.id} thread started")

        try:
            for thread in self.threads:
                thread.join()
        except KeyboardInterrupt:
            self.logger.warning("Simulation interrupted by user. Shutting down...")
            self.stop_event.set()
            for agent in self.agents:
                agent.stop()
                self.logger.debug(f"Agent {agent.id} stopped")
            for thread in self.threads:
                thread.join()
                self.logger.debug(f"Thread {thread.name} joined")
            self.logger.info("Saving env positions")
            write_positions_to_file(self.environment)
            self.logger.info("Saved env positions")
            self.logger.info("Drawing env positions")
            self.environment.draw_gif()
            self.logger.info("Drawed env positions")
        finally:
            self.logger.info("Simulation run terminated")


if __name__ == "__main__":
    area = Polygon([(0, 0), (0, 10), (10, 0)])
    sim = Simulation(5, area)
    sim.run()

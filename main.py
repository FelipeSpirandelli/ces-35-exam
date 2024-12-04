import threading
from typing import List

from shapely import Polygon, Point
import time
from attacker.attacker import AttackAgent
from agents.agent import Agent
from config import Config
from environment.main import Environment
from utils import write_positions_to_file


class Simulation:

    def __init__(self, number_agents: int, area: Polygon, withAttack : bool, attackerPos : Point):
        self.config = Config()
        self.logger = self.config.logger
        self.withAttack = withAttack
        self.number_agents = number_agents
        self.agents: List[Agent] = []
        self.area = area
        self.threads: List[threading.Thread] = []
        self.stop_event = threading.Event()
        self.attacker = None
        self.attackerPos = attackerPos

    def _start_environment(self):
        self.logger.info("Starting environment")
        self.environment = Environment(self.config, self.number_agents, self.area, attackerPresent= self.withAttack, scale=6, attackerPos=self.attackerPos)
        self.logger.debug("Environment started")

    def _start_agents(self):
        self.logger.info("Starting agents")
        for i in range(self.number_agents):
            agent = Agent(i, i == 0, self.config, self.environment)
            self.agents.append(agent)
            initial_position = self.environment.area.centroid
            self.environment.set_position(i, initial_position)
            self.logger.debug(f"Agent {i} initialized at position {initial_position}")

        if (self.withAttack):
            attackerId = self.number_agents
            self.logger.info("Starting attacker agent")
            attacker = AttackAgent(attackerId, False, self.config, self.environment, position=self.attackerPos)
            self.attacker = attacker

    def run(self):
        self.logger.info("Simulation run started")
        self._start_environment()
        self._start_agents()
        self.stop_event = threading.Event()  # Ensure you have a stop event
        for agent in self.agents:
            thread = threading.Thread(target=agent.run, name=f"Agent-Thread-{agent.id}")
            thread.start()
            self.threads.append(thread)
            self.logger.debug(f"Agent {agent.id} thread started")

        if (self.withAttack):
            thread = threading.Thread(target=self.attacker.run, name="Attacker-Thread")
            thread.start()
            self.threads.append(thread)
            self.logger.debug("Attacker thread started")
        try:
            while not self.stop_event.is_set():
                for thread in self.threads:
                    if not thread.is_alive():
                        self.threads.remove(thread)  # Remove completed threads
                
                time.sleep(0.1)
        except KeyboardInterrupt:
            self.logger.warning("Simulation interrupted by user. Shutting down...")
            self.stop_event.set()
            for agent in self.agents:
                agent.stop()  
                self.logger.debug(f"Agent {agent.id} stopped")
            if (self.withAttack):
                self.attacker.stop()
                self.logger.debug("Attacker stopped")

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
    withAttack = True
    attackerPos = Point(8,8)
    area = Polygon([(0, 0), (0, 10), (10, 0)])
    sim = Simulation(5, area, withAttack, attackerPos=attackerPos)
    sim.run()

import math
import random
from threading import Lock
from typing import Dict, List

from shapely import Point, Polygon

from config import Config


class Environment:
    _instance: "Environment" = None
    _initialized: bool = False
    _instance_lock: Lock = Lock()
    _map_lock: Lock = Lock()
    _message_lock: Lock = Lock()

    def __new__(cls, *args, **kwargs) -> "Environment":
        if not cls._instance:
            with cls._instance_lock:
                if not cls._instance:
                    cls._instance = super().__new__(cls)

        return cls._instance

    def __init__(
        self, config: Config = None, number_agents: int = None, area: Polygon = None, scale: float = 5.0
    ):
        if self._initialized:
            return

        if number_agents is None or area is None:
            raise ValueError("Number of agents and/or area not provided")

        self.config = config
        self.logger = self.config.logger

        self.number_agents = number_agents
        self.area = area
        self.scale = scale
        self.agent_to_position: Dict[int, Point] = {}
        self.agent_messages: List[List[Dict]] = [[] for _ in range(number_agents)]
        self.agent_iteration_pos: Dict[List[Point]] = {id: [] for id in range(number_agents)}
        self._initialized = True

    def get_position(self, agent_id) -> Point:
        """Used when an agent needs to know its position"""
        with self._map_lock:
            return self.agent_to_position[agent_id]

    def set_position(self, agent_id: int, position: Point):
        """Used when an agent moves to a new position"""
        with self._map_lock:
            self.agent_iteration_pos[agent_id].append(position)
            self.agent_to_position[agent_id] = position

    def get_area(self) -> Polygon:
        """Returns the area of the environment"""
        return self.area

    def get_messages(self, agent_id: int) -> List[Dict]:
        """Returns all messages for an agent"""
        with self._message_lock:
            messages = self.agent_messages[agent_id]
            self.agent_messages[agent_id] = []
        return messages

    def _check_connection(self, src_id: int, dest_id: int):
        src_pos = self.get_position(src_id)
        dest_pos = self.get_position(dest_id)

        distance = src_pos.distance(dest_pos)
        probability = math.exp(-distance / self.scale)

        self.logger.debug(f"Checking connection between Agent {src_id} and Agent {dest_id}")
        self.logger.debug(f"Source Position: {src_pos}, Destination Position: {dest_pos}")
        self.logger.debug(f"Distance: {distance:.2f}, Connection Probability: {probability:.4f}")

        rand_val = random.random()
        self.logger.debug(f"Random Value: {rand_val:.4f}")

        is_connected = rand_val < probability
        self.logger.debug(f"Connected: {is_connected}")

        return is_connected

    def broadcast_message(self, src_agent_id: int, message: Dict):
        self.logger.debug(f"Broadcasting message from Agent {src_agent_id}: {message}")
        with self._message_lock:
            for agent_id in range(self.number_agents):
                if agent_id != src_agent_id:
                    if self._check_connection(src_agent_id, agent_id):
                        self.agent_messages[agent_id].append(message)
                        self.logger.debug(f"Message sent to Agent {agent_id}")
                    else:
                        self.logger.debug(f"Message not sent to Agent {agent_id} due to connection failure")

    def draw_gif(self):
        import matplotlib.pyplot as plt
        from matplotlib.animation import FuncAnimation

        # Extract polygon coordinates
        x, y = self.area.exterior.xy

        # Get the number of iterations from the agent positions
        number_iterations = len(next(iter(self.agent_iteration_pos.values())))

        # Set up the plot
        fig, ax = plt.subplots()
        ax.plot(x, y, color="black")

        # Set plot limits
        ax.set_xlim(min(x) - 1, max(x) + 1)
        ax.set_ylim(min(y) - 1, max(y) + 1)

        colors = ["r", "g", "b", "c", "m", "y", "k", "w"]

        # Initialize agent scatter plots
        agent_plots = []
        for positions, color in zip(self.agent_iteration_pos.values(), colors):
            # Get initial position
            pos = positions[0]
            # Plot the initial position of the agent
            (agent_plot,) = ax.plot([pos.x], [pos.y], "o", color=color)
            agent_plots.append(agent_plot)

        # Update function for animation
        def update(frame):
            for agent_plot, positions in zip(agent_plots, self.agent_iteration_pos.values()):
                pos = positions[frame]
                agent_plot.set_data([pos.x], [pos.y])  # Wrap pos.x and pos.y in lists
            return agent_plots

        # Create the animation
        ani = FuncAnimation(fig, update, frames=number_iterations, blit=True, interval=1000)

        # Save the animation as a GIF
        ani.save("agents_animation.gif", writer="pillow")

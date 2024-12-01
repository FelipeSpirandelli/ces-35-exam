from shapely import Point

from agents.movement import Movement
from config import Config
from environment.main import Environment


class Communication:

    def __init__(self, agent_id: int, config: Config, env: Environment):
        self.agent_id = agent_id
        self.env = env
        self.logger = config.logger

    def send_my_leader_position(self, timestamp: int):
        pos = self.env.get_position(self.agent_id)
        self.logger.debug(f"Sending my leader position: {pos} with timestamp {timestamp}")
        self.send_leader_position(pos, timestamp)

    def send_leader_position(self, leader_pos: Point, timestamp: int):
        if leader_pos is None:
            self.logger.warning("Attempted to send leader position, but leader_pos is None")
            return
        message = {
            "message_type": 1,
            "src_id": self.agent_id,
            "leader_pos": leader_pos,
            "timestamp": timestamp,
        }
        self.env.broadcast_message(self.agent_id, message)
        self.logger.info(f"Broadcasted leader position: {leader_pos} with timestamp {timestamp}")


def communication_factory(agent_id: int, config: Config = None, env: Environment = None) -> Movement:
    return Communication(agent_id, config or Config(), env or Environment())

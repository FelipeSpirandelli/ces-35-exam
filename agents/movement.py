from shapely import Point

from config import Config
from environment.main import Environment


class Movement:

    MAX_MOV_SPEED = 1
    DEFAULT_MOV_SPEED = 0.5

    def __init__(self, agent_id: int, config: Config, env: Environment):
        self.agent_id = agent_id
        self.config = config
        self.logger = self.config.logger
        self.env = env

    def _set_position(self, position: Point):
        self.logger.debug(f"Setting new position: {position}")
        self.env.set_position(self.agent_id, position)

    def move_follower(self, leader_pos: Point):
        self.logger.debug(f"Moving follower towards {leader_pos}")
        cur_pos = self.env.get_position(self.agent_id)
        if not leader_pos:
            self.logger.warning("Leader position is None, cannot move follower")
            self._set_position(cur_pos)
            return cur_pos
        new_pos = self._travel_point(cur_pos, leader_pos)
        self._set_position(new_pos)
        self.logger.info(f"Follower moved to {new_pos}")
        return new_pos

    def move_leader(self):
        self.logger.debug("Moving leader")
        cur_pos = self.env.get_position(self.agent_id)
        area = self.env.get_area()

        current_distance = area.exterior.project(cur_pos)
        next_distance = (current_distance + self.DEFAULT_MOV_SPEED) % area.exterior.length
        next_point = area.exterior.interpolate(next_distance)

        new_pos = self._travel_point(cur_pos, next_point, self.DEFAULT_MOV_SPEED)
        self._set_position(new_pos)
        self.logger.info(f"Leader moved to {new_pos}")
        return new_pos

    def _travel_point(self, start: Point, target: Point, max_distance: float = MAX_MOV_SPEED) -> Point:
        self.logger.debug(f"Traveling from {start} to {target} with max distance {max_distance}")
        total_distance = start.distance(target)

        if total_distance <= max_distance:
            self.logger.debug("Target within max distance, moving directly to target")
            return target

        direction_x = target.x - start.x
        direction_y = target.y - start.y
        scale = max_distance / total_distance

        new_x = start.x + direction_x * scale
        new_y = start.y + direction_y * scale

        new_pos = Point(new_x, new_y)
        self.logger.debug(f"New position after traveling: {new_pos}")
        return new_pos


def movement_factory(agent_id: int, config: Config = None, env: Environment = None) -> Movement:
    return Movement(agent_id, config or Config(), env or Environment())

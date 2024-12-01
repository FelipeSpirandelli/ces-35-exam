from threading import Event, Thread
from time import sleep

from agents.communication import Communication, communication_factory
from agents.movement import Movement, movement_factory
from config import Config
from environment.main import Environment


class Agent:

    def __init__(
        self,
        id: int,
        is_leader: bool,
        config: Config,
        env: Environment = None,
        communication: Communication = None,
        movement: Movement = None,
    ):
        self.id = id
        self.is_leader = is_leader
        self.env = env
        self.config = config
        self.communication = communication or communication_factory(self.id)
        self.movement = movement or movement_factory(self.id)
        self.leader_pos = None
        self.leader_pos_timestamp = 0
        self.stop_event = Event()
        self.listener_thread = None
        self.logger = self.config.get_agent_logger(self.id)

    def communicate(self):
        if self.is_leader:
            self.leader_pos_timestamp += 1
            self.logger.debug(f"Leader sending position with timestamp {self.leader_pos_timestamp}")
            self.communication.send_my_leader_position(self.leader_pos_timestamp)
        else:
            self.logger.debug(
                f"Follower sending leader position: {self.leader_pos} at timestamp {self.leader_pos_timestamp}"  # noqa: E501
            )
            self.communication.send_leader_position(self.leader_pos, self.leader_pos_timestamp)

    def move(self):
        if self.is_leader:
            self.logger.debug("Leader moving")
            self.movement.move_leader()
        else:
            self.logger.debug(f"Follower moving towards {self.leader_pos}")
            self.movement.move_follower(self.leader_pos)

    def listen_for_messages(self):
        def _listen():
            self.logger.info("Listener thread started")
            while not self.stop_event.is_set():
                for message in self.env.get_messages(self.id):
                    message_type = message["message_type"]
                    if message_type == 1:
                        rcv_leader_pos = message["leader_pos"]
                        rcv_leader_pos_timestamp = message["timestamp"]
                        rcv_src_id = message["src_id"]
                        self.logger.debug(
                            f"Received message type 1 from Agent {rcv_src_id}: "
                            f"Position={rcv_leader_pos}, Timestamp={rcv_leader_pos_timestamp}"
                        )
                        if not self.is_leader and (
                            rcv_leader_pos_timestamp > self.leader_pos_timestamp or rcv_src_id == 0
                        ):
                            self.leader_pos = rcv_leader_pos
                            self.leader_pos_timestamp = rcv_leader_pos_timestamp
                            self.logger.info(
                                f"Updated leader position to {self.leader_pos} with timestamp {self.leader_pos_timestamp}"  # noqa: E501
                            )
                sleep(0.1)
            self.logger.info("Listener thread stopping")

        self.listener_thread = Thread(target=_listen, name=f"Listener-Thread-{self.id}")
        self.listener_thread.start()

    def _iterate(self):
        self.logger.debug("Agent iteration started")
        self.communicate()
        self.move()
        self.logger.debug("Agent iteration completed")

    def run(self):
        self.logger.info("Agent run started")
        self.listen_for_messages()
        try:
            while not self.stop_event.is_set():
                self._iterate()
                sleep(0.3)
        except Exception as e:
            self.logger.error(f"Agent {self.id} encountered an error: {e}", exc_info=True)
        finally:
            if self.listener_thread:
                self.logger.info("Waiting for listener thread to join")
                self.listener_thread.join()
            self.logger.info("Agent run terminated")

    def stop(self):
        self.logger.info("Stopping agent")
        self.stop_event.set()
        if self.listener_thread:
            self.listener_thread.join()
            self.logger.info("Listener thread successfully joined")

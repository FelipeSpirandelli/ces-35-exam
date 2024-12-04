from threading import Event, Thread
from time import sleep
from agents.communication import Communication
from agents.movement import Movement
from config import Config
from environment.main import Environment
from agents.agent import Agent  # Import the base class
from shapely import Point

class AttackAgent(Agent):

    def __init__(
        self,
        id: int,
        is_leader: bool,
        config: Config,
        env: Environment = None,
        communication: Communication = None,
        movement: Movement = None,
        position : Point = None
    ):
        super().__init__(id, is_leader, config, env, communication, movement)
        self.attack_mode = True
        self.default_pos  = position
        self.fake_timestamp = 9999

    def communicate(self):
        # Customize the communication behavior for the attack agent
        if self.attack_mode:
            self.logger.debug(f"Agent {self.id} is in attack mode, sending attack message.")
            self.communication.broadcast_generic_message(
                message={
                    "message_type" : 1,
                    "src_id" : self.id,
                    "leader_pos": self.default_pos,
                    "timestamp": self.fake_timestamp
                }
            )
            self.fake_timestamp += 100
            
        else:
            # super().communicate()
            pass

    '''def move(self):
        # Customize the movement behavior for the attack agent
        if self.attack_mode:
            self.logger.debug(f"Agent {self.id} attacking target.")
            self.movement.attack_target()
        else:
            super().move()  # Use the base class behavior
    '''
    def enable_attack_mode(self):
        self.logger.info(f"Agent {self.id} enabling attack mode.")
        self.attack_mode = True

    def disable_attack_mode(self):
        self.logger.info(f"Agent {self.id} disabling attack mode.")
        self.attack_mode = False

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
        self.logger.debug("Attacker iteration started")
        self.communicate()
        #self.move()
        self.logger.debug("Attacker iteration completed")

    def run(self):
        self.logger.info("Attacker run started")
        #self.listen_for_messages()
        try:
            while not self.stop_event.is_set():
                self._iterate()
                sleep(0.25)
        except Exception as e:
            self.logger.error(f"Attacker with id {self.id} encountered an error: {e}", exc_info=True)
        finally:
            if self.listener_thread:
                self.logger.info("Waiting for attacker listener thread to join") # not used
                self.listener_thread.join()
            self.logger.info("Attacker run terminated")

    def stop(self):
        self.logger.info("Stopping attacker")
        self.stop_event.set()
        if self.listener_thread:
            self.listener_thread.join()
            self.logger.info("Listener thread successfully joined")
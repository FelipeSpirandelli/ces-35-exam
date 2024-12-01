from environment.main import Environment


def write_positions_to_file(env: Environment):
    for agent_id in env.agent_iteration_pos:
        with open(f"data/agent_{agent_id}_positions.txt", "w") as f:
            for position in env.agent_iteration_pos[agent_id]:
                f.write(f"{position.x},{position.y}\n")

# Project README: Multi-Agent Simulation System

## Overview

This project is a **Multi-Agent Simulation System** where agents interact with their environment and each other to perform specific tasks. The simulation includes agent movement, communication, and interaction with a shared environment. It is designed for flexibility, extensibility, and detailed logging.

---

## Setup

### Prerequisites

1. Install [Poetry](https://python-poetry.org/).
2. Ensure Python 3.9+ is installed on your system.

### Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd <repository-directory>
   ```
2. Use Poetry to install dependencies:
   ```bash
   poetry install
   ```

---

## How to Run

### Running the Simulation

1. Activate the Poetry environment:
   ```bash
   poetry shell
   ```
2. Execute the `main.py` file:
   ```bash
   python main.py
   ```
   The simulation will start, initializing the environment and agents.

---

## Simulation

The simulation involves the coordination of multiple agents within a shared environment. It is initialized through the `Simulation` class (`simulation/main.py`) and follows these steps:

1. **Initialize Environment**: Set up the shared space for agents.
2. **Create Agents**: Instantiate agents with unique IDs and roles.
3. **Start Threads**: Each agent runs in its thread to enable concurrent operation.
4. **Agent Actions**: Agents perform communication and movement tasks iteratively.

### Key Features

- **Asynchronous Agent Behavior**: Each agent runs independently, reacting to the environment and other agents.
- **Dynamic Environment Updates**: Positions and messages are updated and exchanged in real-time.
- **Logging**: Detailed logs for debugging and analysis.

---

## Environment

The `Environment` class manages the shared simulation space, ensuring proper coordination between agents.

### Features

- **Area Definition**: The environment is a polygonal area within which agents operate.
- **Agent Positioning**: Tracks and updates agent positions.
- **Message Broadcasting**: Facilitates communication by broadcasting messages between agents.
- **Connection Simulation**: Determines message delivery based on distance and probabilistic connection checks.

### Usage

The environment is automatically initialized during the simulation setup, ensuring consistency and scalability.

---

## Agent Logic

The `Agent` class defines the behavior of individual agents, including:

1. **Movement**: Follows leader-follower dynamics.
2. **Communication**: Agents exchange messages to synchronize actions.
3. **Interaction**: Agents interact with the environment to move and receive messages.

### Movement

- **Leader**: Moves autonomously along the perimeter of the environment.
- **Follower**: Adjusts position based on the leader's location.
- Implemented in the `Movement` class (`movement.py`).

### Communication

- **Leader**: Broadcasts its position periodically.
- **Follower**: Responds to leader updates and shares its knowledge.
- Implemented in the `Communication` class (`communication.py`).

### Execution Flow

1. **Listening Thread**: Each agent runs a thread to receive messages continuously.
2. **Iteration Loop**: Agents communicate, move, and log updates in a continuous loop.

---

## Logger

The `Logger` is a core component of the system, providing detailed output for debugging and analysis. Each agent has its dedicated logger to ensure separation of concerns.

### Features

- **Thread-Safe Logging**: Ensures logs are captured even in concurrent environments.
- **Agent-Specific Logs**: Separate log files for each agent.
- **Detailed Messages**: Logs include timestamps, thread names, and file/line information for clarity.

### Logging Levels

- `DEBUG`: For development and detailed insights.
- `INFO`: For high-level events.
- `WARNING`: For potential issues or unexpected behavior.
- `ERROR`: For critical issues during simulation.

---

## Example Simulation

- **Setup**: A polygonal area (triangle) with 5 agents.
- **Execution**:

  - One leader moves autonomously.
  - Four followers adjust positions based on the leader's updates.
  - Communication happens dynamically with connection probabilities.

- **Result**: The simulation generates logs and creates a GIF visualizing agent movements (`agents_animation.gif`).

---

## Visual Output

The simulation produces a GIF animation of the agents' movement within the environment. This visual representation helps analyze agent behavior and interactions.

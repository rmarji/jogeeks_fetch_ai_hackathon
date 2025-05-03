import os
import sys
import time
import asyncio
import subprocess
from typing import List, Dict, Any
import signal
import argparse

# Parse command line arguments
parser = argparse.ArgumentParser(description='Run the DeFi Price Monitoring and Alert System')
parser.add_argument('--agents', nargs='+', choices=['price', 'analysis', 'alert', 'user', 'all'], 
                    default=['all'], help='Specify which agents to run')
parser.add_argument('--debug', action='store_true', help='Enable debug mode with more verbose output')
args = parser.parse_args()

# Configuration
AGENTS = {
    'price': {
        'name': 'Price Agent',
        'file': 'agents/price_agent.py',
        'port': 8001,
        'dependencies': []
    },
    'analysis': {
        'name': 'Analysis Agent',
        'file': 'agents/analysis_agent.py',
        'port': 8002,
        'dependencies': ['price']
    },
    'alert': {
        'name': 'Alert Agent',
        'file': 'agents/alert_agent.py',
        'port': 8003,
        'dependencies': ['analysis']
    },
    'user': {
        'name': 'User Agent',
        'file': 'agents/user_agent.py',
        'port': 8004,
        'dependencies': ['price', 'analysis', 'alert']
    }
}

# Global variables
processes: Dict[str, subprocess.Popen] = {}
agent_addresses: Dict[str, str] = {}
running = True


def signal_handler(sig, frame):
    """Handle Ctrl+C to gracefully shut down all agents."""
    global running
    print("\nShutting down all agents...")
    running = False
    stop_all_agents()
    sys.exit(0)


def start_agent(agent_key: str) -> subprocess.Popen:
    """Start an agent process."""
    agent_info = AGENTS[agent_key]
    
    # Check if all dependencies are running
    for dep in agent_info['dependencies']:
        if dep not in agent_addresses:
            print(f"Cannot start {agent_info['name']} because {AGENTS[dep]['name']} is not running")
            return None
    
    # Prepare environment variables for the agent
    env = os.environ.copy()
    
    # Add the current directory to PYTHONPATH to allow imports from the project root
    if 'PYTHONPATH' in env:
        env['PYTHONPATH'] = f"{os.getcwd()}:{env['PYTHONPATH']}"
    else:
        env['PYTHONPATH'] = os.getcwd()
    
    # Add agent addresses to environment
    for dep in agent_info['dependencies']:
        env[f"{dep.upper()}_AGENT_ADDRESS"] = agent_addresses[dep]
    
    # Start the agent process
    print(f"Starting {agent_info['name']}...")
    
    # Use python executable from the current environment
    python_exe = sys.executable
    
    # Start the process
    process = subprocess.Popen(
        [python_exe, agent_info['file']],
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,
        universal_newlines=True
    )
    
    return process


def monitor_agent_output(agent_key: str, process: subprocess.Popen):
    """Monitor the output of an agent process and extract its address."""
    agent_info = AGENTS[agent_key]
    
    # Read the output line by line
    for line in iter(process.stdout.readline, ''):
        # Print the output
        if args.debug:
            # In debug mode, print all output
            print(f"[{agent_info['name']}] {line.strip()}")
        elif "address" in line.lower() or "price" in line.lower() or "alert" in line.lower() or "notification" in line.lower():
            # In regular mode, print only important information
            print(f"[{agent_info['name']}] {line.strip()}")
        
        # Extract the agent address
        if "address" in line.lower():
            # Find the agent address in the output
            parts = line.split()
            for i, part in enumerate(parts):
                if part.lower().startswith("address:"):
                    if i + 1 < len(parts):
                        address = parts[i + 1]
                        agent_addresses[agent_key] = address
                        print(f"Detected {agent_info['name']} address: {address}")
                        break
        
        # Check if the process is still running
        if process.poll() is not None:
            break


def stop_agent(agent_key: str):
    """Stop an agent process."""
    if agent_key in processes and processes[agent_key]:
        print(f"Stopping {AGENTS[agent_key]['name']}...")
        processes[agent_key].terminate()
        processes[agent_key].wait(timeout=5)
        processes[agent_key] = None


def stop_all_agents():
    """Stop all running agent processes."""
    # Stop agents in reverse dependency order
    for agent_key in reversed(list(processes.keys())):
        stop_agent(agent_key)


def start_agents(agent_keys: List[str]):
    """Start the specified agents."""
    # Start agents in dependency order
    for agent_key in agent_keys:
        if agent_key not in processes or not processes[agent_key]:
            process = start_agent(agent_key)
            if process:
                processes[agent_key] = process
                # Start a thread to monitor the agent output
                import threading
                thread = threading.Thread(target=monitor_agent_output, args=(agent_key, process))
                thread.daemon = True
                thread.start()
                
                # Wait longer for the agent to start and print its address
                time.sleep(5)


def main():
    """Main function to run the agents."""
    # Set up signal handler for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    
    # Determine which agents to run
    agent_keys = []
    if 'all' in args.agents:
        agent_keys = list(AGENTS.keys())
    else:
        agent_keys = args.agents
    
    # Sort agents by dependencies
    sorted_agents = []
    while agent_keys:
        for agent_key in list(agent_keys):
            # Check if all dependencies are in sorted_agents
            if all(dep in sorted_agents for dep in AGENTS[agent_key]['dependencies']):
                sorted_agents.append(agent_key)
                agent_keys.remove(agent_key)
    
    # Start the agents
    start_agents(sorted_agents)
    
    # Keep the main thread running
    try:
        while running:
            # Check if any agent has crashed
            for agent_key, process in list(processes.items()):
                if process and process.poll() is not None:
                    print(f"{AGENTS[agent_key]['name']} has crashed. Exit code: {process.returncode}")
                    # Restart the agent
                    stop_agent(agent_key)
                    time.sleep(1)
                    start_agents([agent_key])
            
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down all agents...")
        stop_all_agents()


if __name__ == "__main__":
    main()

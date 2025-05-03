# Gas Fee Monitor Agent

A simple agent that monitors Ethereum gas prices and alerts users when gas fees drop below a specified threshold.

## Overview

This project demonstrates the capabilities of the Agentverse platform by implementing a practical DeFi tool that helps users monitor Ethereum gas prices. The Gas Fee Monitor Agent periodically checks current gas prices using a public API, compares them against user-defined thresholds, and sends notifications when gas prices are favorable for transactions.

### Key Features

- **Real-time Gas Price Monitoring**: Fetch Ethereum gas prices from public APIs
- **Customizable Thresholds**: Set your own thresholds for low, medium, and high gas prices
- **Smart Notifications**: Receive alerts when gas prices drop to favorable levels
- **Historical Data**: Store and analyze historical gas price data
- **Simple API**: Request current gas prices and historical data programmatically

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Setup

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd sample-project-2-gas-fee-monitor
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file from the template:
   ```bash
   cp .env.template .env
   ```

5. Edit the `.env` file to add your API keys and customize settings:
   ```
   # API Keys for Ethereum gas price data
   ETHERSCAN_API_KEY=your_etherscan_api_key_here
   
   # Gas price thresholds (in Gwei)
   LOW_THRESHOLD=20
   MEDIUM_THRESHOLD=50
   HIGH_THRESHOLD=100
   ```

## Usage

### Running the Gas Monitor Agent

To start the Gas Monitor Agent:

```bash
python gas_monitor_agent.py
```

The agent will start monitoring gas prices at the interval specified in your `.env` file (default: every 60 seconds).

### Using the Client

A sample client is provided to demonstrate how to interact with the Gas Monitor Agent:

```bash
python client.py
```

Before running the client, make sure to set the `GAS_MONITOR_ADDRESS` environment variable to the address of your running Gas Monitor Agent. You can find this address in the agent's startup logs.

### API Endpoints

The Gas Monitor Agent provides the following API endpoints:

#### Get Current Gas Price

Request the current Ethereum gas price:

```python
await ctx.send(GAS_MONITOR_ADDRESS, GetGasPriceRequest())
```

#### Set Custom Thresholds

Set custom gas price thresholds:

```python
thresholds = GasPriceThresholds(
    low_threshold=15.0,
    medium_threshold=40.0,
    high_threshold=80.0
)
await ctx.send(GAS_MONITOR_ADDRESS, SetThresholdsRequest(thresholds=thresholds))
```

#### Get Historical Data

Request historical gas price data:

```python
await ctx.send(GAS_MONITOR_ADDRESS, GetHistoricalDataRequest(hours=24))
```

## How It Works

### Gas Price Levels

The agent categorizes gas prices into four levels:

- **LOW**: Below the low threshold (default: 20 Gwei)
- **MEDIUM**: Between the low and medium thresholds (default: 20-50 Gwei)
- **HIGH**: Between the medium and high thresholds (default: 50-100 Gwei)
- **VERY_HIGH**: Above the high threshold (default: 100+ Gwei)

### Notification Logic

The agent sends notifications in the following cases:

1. When gas prices drop to the LOW level
2. When gas prices rise from the LOW level to a higher level
3. When gas prices drop from the VERY_HIGH level to a lower level

### Data Storage

The agent stores:

1. **Historical Gas Prices**: Up to 1000 data points (approximately 16.7 hours at 1-minute intervals)
2. **Notifications**: Up to 100 most recent notifications
3. **User Preferences**: Custom thresholds and notification settings

## Project Structure

```
sample-project-2-gas-fee-monitor/
├── README.md                 # Project documentation
├── .env.template             # Template for environment variables
├── requirements.txt          # Dependencies
├── models.py                 # Data models for the agent
├── gas_monitor_agent.py      # Main agent implementation
└── client.py                 # Sample client for interacting with the agent
```

## Extension Ideas

Here are some ways to extend this project:

1. **Multi-chain Support**: Expand to monitor gas fees on other EVM-compatible chains like Polygon, Arbitrum, or Optimism
2. **Transaction Automation**: Trigger transactions when gas prices are favorable
3. **Advanced Notifications**: Add email, SMS, or messaging platform integration
4. **Prediction Model**: Implement a simple model to predict gas price movements
5. **Web Dashboard**: Create a simple visualization of gas price trends
6. **Mobile App Integration**: Build a mobile app that receives push notifications
7. **Gas Price Comparison**: Compare gas prices across different chains or providers

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [Fetch.ai](https://fetch.ai/) for the uAgents framework
- [Etherscan](https://etherscan.io/) for the Ethereum gas price API

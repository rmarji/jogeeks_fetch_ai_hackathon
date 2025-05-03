import os
import numpy as np
import pandas as pd
from datetime import datetime
from typing import Dict, List, Optional, Tuple

from dotenv import load_dotenv
from uagents import Agent, Context
from uagents.experimental.quota import QuotaProtocol, RateLimit

from protocols.price_data import PriceData, PriceRequest, PriceResponse, PriceUpdate
from protocols.analysis import (
    AnalysisRequest, 
    AnalysisResponse, 
    AnalysisResult,
    TrendDirection,
    SignalType,
    SignalStrength
)

# Load environment variables
load_dotenv()

# Agent configuration
AGENT_SEED = os.getenv("ANALYSIS_AGENT_SEED", "analysis-agent-seed")
AGENT_PORT = int(os.getenv("ANALYSIS_AGENT_PORT", "8002"))
AGENT_ENDPOINT = f"http://localhost:{AGENT_PORT}/submit"

# Price agent address (this would be set after the price agent is running)
PRICE_AGENT_ADDRESS = os.getenv("PRICE_AGENT_ADDRESS", "agent1qtawh5k0a6uns5dwa3sgf0gff945prv3zc44yvvlj0yv8utlt5h6xq89qm8")

# Create the agent
analysis_agent = Agent(
    name="analysis-agent",
    seed=AGENT_SEED,
    port=AGENT_PORT,
    endpoint=AGENT_ENDPOINT,
)

# Create a protocol with rate limiting
analysis_protocol = QuotaProtocol(
    storage_reference=analysis_agent.storage,
    name="Analysis-Protocol",
    version="0.1.0",
    default_rate_limit=RateLimit(window_size_minutes=1, max_requests=10),
)


def calculate_moving_averages(prices: List[float], short_window: int = 5, long_window: int = 20) -> Tuple[float, float]:
    """
    Calculate short and long moving averages from a list of prices.
    
    Args:
        prices: List of historical prices
        short_window: Window size for short moving average
        long_window: Window size for long moving average
        
    Returns:
        Tuple of (short_ma, long_ma)
    """
    if len(prices) < long_window:
        # Not enough data for long window, use available data
        long_window = len(prices)
    
    if len(prices) < short_window:
        # Not enough data for short window, use available data
        short_window = len(prices)
    
    short_ma = np.mean(prices[-short_window:]) if short_window > 0 else prices[-1]
    long_ma = np.mean(prices[-long_window:]) if long_window > 0 else prices[-1]
    
    return short_ma, long_ma


def calculate_rsi(prices: List[float], window: int = 14) -> float:
    """
    Calculate the Relative Strength Index (RSI) from a list of prices.
    
    Args:
        prices: List of historical prices
        window: RSI calculation window
        
    Returns:
        RSI value (0-100)
    """
    if len(prices) < window + 1:
        # Not enough data, return neutral RSI
        return 50.0
    
    # Calculate price changes
    deltas = np.diff(prices)
    
    # Calculate gains and losses
    gains = np.clip(deltas, 0, None)
    losses = np.clip(-deltas, 0, None)
    
    # Calculate average gains and losses
    avg_gain = np.mean(gains[-window:])
    avg_loss = np.mean(losses[-window:])
    
    if avg_loss == 0:
        # No losses, RSI is 100
        return 100.0
    
    # Calculate RS and RSI
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    
    return rsi


def calculate_macd(prices: List[float], fast_window: int = 12, slow_window: int = 26, signal_window: int = 9) -> Tuple[float, float]:
    """
    Calculate the Moving Average Convergence Divergence (MACD) from a list of prices.
    
    Args:
        prices: List of historical prices
        fast_window: Fast EMA window
        slow_window: Slow EMA window
        signal_window: Signal line window
        
    Returns:
        Tuple of (macd_line, signal_line)
    """
    if len(prices) < slow_window:
        # Not enough data, return neutral MACD
        return 0.0, 0.0
    
    # Calculate EMAs
    df = pd.DataFrame(prices, columns=['price'])
    df['ema_fast'] = df['price'].ewm(span=fast_window, adjust=False).mean()
    df['ema_slow'] = df['price'].ewm(span=slow_window, adjust=False).mean()
    
    # Calculate MACD line
    df['macd'] = df['ema_fast'] - df['ema_slow']
    
    # Calculate signal line
    df['signal'] = df['macd'].ewm(span=signal_window, adjust=False).mean()
    
    # Get the latest values
    macd_line = df['macd'].iloc[-1]
    signal_line = df['signal'].iloc[-1]
    
    return macd_line, signal_line


def determine_trend(prices: List[float], short_ma: float, long_ma: float) -> TrendDirection:
    """
    Determine the price trend based on moving averages and recent price action.
    
    Args:
        prices: List of historical prices
        short_ma: Short-term moving average
        long_ma: Long-term moving average
        
    Returns:
        TrendDirection enum value
    """
    if len(prices) < 2:
        # Not enough data to determine trend
        return TrendDirection.SIDEWAYS
    
    # Check if short MA is above long MA (bullish)
    if short_ma > long_ma:
        return TrendDirection.UP
    
    # Check if short MA is below long MA (bearish)
    elif short_ma < long_ma:
        return TrendDirection.DOWN
    
    # If MAs are very close, check recent price action
    else:
        # Calculate recent price change
        recent_change = (prices[-1] - prices[-2]) / prices[-2]
        
        if recent_change > 0.01:  # 1% increase
            return TrendDirection.UP
        elif recent_change < -0.01:  # 1% decrease
            return TrendDirection.DOWN
        else:
            return TrendDirection.SIDEWAYS


def generate_trading_signal(
    trend: TrendDirection, 
    rsi: float, 
    macd: float, 
    signal: float
) -> Tuple[SignalType, SignalStrength]:
    """
    Generate a trading signal based on technical indicators.
    
    Args:
        trend: Current price trend
        rsi: Relative Strength Index value
        macd: MACD line value
        signal: MACD signal line value
        
    Returns:
        Tuple of (SignalType, SignalStrength)
    """
    # Initialize signal counters
    buy_signals = 0
    sell_signals = 0
    
    # Check trend
    if trend == TrendDirection.UP:
        buy_signals += 1
    elif trend == TrendDirection.DOWN:
        sell_signals += 1
    
    # Check RSI
    if rsi < 30:  # Oversold
        buy_signals += 1
    elif rsi > 70:  # Overbought
        sell_signals += 1
    
    # Check MACD
    if macd > signal and macd > 0:  # Bullish crossover
        buy_signals += 1
    elif macd < signal and macd < 0:  # Bearish crossover
        sell_signals += 1
    
    # Determine signal type
    if buy_signals > sell_signals:
        signal_type = SignalType.BUY
    elif sell_signals > buy_signals:
        signal_type = SignalType.SELL
    else:
        signal_type = SignalType.HOLD
    
    # Determine signal strength
    signal_count = max(buy_signals, sell_signals)
    if signal_count >= 3:
        signal_strength = SignalStrength.STRONG
    elif signal_count == 2:
        signal_strength = SignalStrength.MODERATE
    else:
        signal_strength = SignalStrength.WEAK
    
    return signal_type, signal_strength


async def analyze_price_data(ctx: Context, symbol: str) -> Optional[AnalysisResult]:
    """
    Perform technical analysis on historical price data for a cryptocurrency.
    
    Args:
        ctx: Agent context
        symbol: Cryptocurrency symbol
        
    Returns:
        AnalysisResult object or None if analysis fails
    """
    # Get historical data from storage
    historical_data = ctx.storage.get("historical_data")
    if historical_data is None:
        historical_data = {}
    
    if symbol not in historical_data or not historical_data[symbol]:
        ctx.logger.warning(f"No historical data available for {symbol}")
        
        # Try to fetch current price from price agent
        if PRICE_AGENT_ADDRESS:
            ctx.logger.info(f"Requesting current price for {symbol} from price agent")
            
            try:
                # Request price data from price agent
                await ctx.send(PRICE_AGENT_ADDRESS, PriceRequest(symbols=[symbol]))
                
                # We'll handle the response in the price response handler
                return None
            except Exception as e:
                ctx.logger.error(f"Error requesting price data: {e}")
                return None
        else:
            ctx.logger.error("Price agent address not configured")
            return None
    
    # Extract prices from historical data
    prices = [entry["price"] for entry in historical_data[symbol]]
    
    if not prices:
        ctx.logger.warning(f"No price data available for {symbol}")
        return None
    
    # Get current price (latest in the historical data)
    current_price = prices[-1]
    
    # Calculate technical indicators
    short_ma, long_ma = calculate_moving_averages(prices)
    rsi = calculate_rsi(prices)
    macd, signal_line = calculate_macd(prices)
    
    # Determine trend
    trend = determine_trend(prices, short_ma, long_ma)
    
    # Generate trading signal
    signal_type, signal_strength = generate_trading_signal(trend, rsi, macd, signal_line)
    
    # Create analysis result
    result = AnalysisResult(
        symbol=symbol,
        current_price=current_price,
        timestamp=datetime.utcnow().isoformat(),
        moving_avg_short=short_ma,
        moving_avg_long=long_ma,
        rsi=rsi,
        macd=macd,
        macd_signal=signal_line,
        trend=trend,
        signal=signal_type,
        signal_strength=signal_strength,
    )
    
    return result


@analysis_agent.on_event("startup")
async def startup(ctx: Context):
    """
    Initialize the analysis agent on startup.
    """
    ctx.logger.info(f"Analysis Agent started with address: {analysis_agent.address}")
    
    # Initialize storage for historical data if it doesn't exist
    if not ctx.storage.get("historical_data"):
        ctx.storage.set("historical_data", {})
    
    # Initialize storage for analysis results if it doesn't exist
    if not ctx.storage.get("analysis_results"):
        ctx.storage.set("analysis_results", {})
    
    # Register with price agent if address is available
    if PRICE_AGENT_ADDRESS:
        ctx.logger.info(f"Registering with price agent at {PRICE_AGENT_ADDRESS}")
        
        # Store the price agent address
        ctx.storage.set("price_agent_address", PRICE_AGENT_ADDRESS)
        
        # Request initial price data for default cryptocurrencies
        default_cryptos = os.getenv("DEFAULT_CRYPTOCURRENCIES", "BTC,ETH,SOL,AVAX,DOT").split(",")
        ctx.logger.info(f"Requesting initial price data for: {', '.join(default_cryptos)}")
        
        try:
            # Request price data from price agent
            await ctx.send(PRICE_AGENT_ADDRESS, PriceRequest(symbols=default_cryptos))
        except Exception as e:
            ctx.logger.error(f"Error requesting initial price data: {e}")


@analysis_agent.on_message(model=PriceUpdate)
async def handle_price_update(ctx: Context, sender: str, msg: PriceUpdate):
    """
    Handle price updates from the price agent.
    """
    price_data = msg.data
    symbol = price_data.symbol
    
    ctx.logger.info(f"Received price update for {symbol}: ${price_data.price:.2f}")
    
    # Update historical data
    historical_data = ctx.storage.get("historical_data")
    if historical_data is None:
        historical_data = {}
    
    if symbol not in historical_data:
        historical_data[symbol] = []
    
    # Add the new price data to the historical data
    historical_data[symbol].append({
        "price": price_data.price,
        "timestamp": price_data.timestamp,
        "volume_24h": price_data.volume_24h,
        "percent_change_24h": price_data.percent_change_24h,
    })
    
    # Keep only the last 100 data points to avoid excessive storage
    if len(historical_data[symbol]) > 100:
        historical_data[symbol] = historical_data[symbol][-100:]
    
    # Save the updated historical data
    ctx.storage.set("historical_data", historical_data)
    
    # Perform analysis on the updated data
    analysis_result = await analyze_price_data(ctx, symbol)
    
    if analysis_result:
        ctx.logger.info(f"Analysis for {symbol}: {analysis_result}")
        
        # Store the analysis result
        analysis_results = ctx.storage.get("analysis_results")
        if analysis_results is None:
            analysis_results = {}
        analysis_results[symbol] = analysis_result.dict()
        ctx.storage.set("analysis_results", analysis_results)
        
        # Broadcast the analysis result to alert agent
        # This would be implemented if we had an alert agent address
        alert_agent_address = ctx.storage.get("alert_agent_address")
        if alert_agent_address:
            ctx.logger.info(f"Sending analysis result for {symbol} to alert agent")
            await ctx.send(alert_agent_address, analysis_result)


@analysis_agent.on_message(model=PriceResponse)
async def handle_price_response(ctx: Context, sender: str, msg: PriceResponse):
    """
    Handle price responses from the price agent.
    """
    ctx.logger.info(f"Received price response from {sender} with {len(msg.prices)} symbols")
    
    # Update historical data with the received prices
    historical_data = ctx.storage.get("historical_data")
    if historical_data is None:
        historical_data = {}
    
    for symbol, price_data in msg.prices.items():
        if symbol not in historical_data:
            historical_data[symbol] = []
        
        # Add the new price data to the historical data
        historical_data[symbol].append({
            "price": price_data.price,
            "timestamp": price_data.timestamp,
            "volume_24h": price_data.volume_24h,
            "percent_change_24h": price_data.percent_change_24h,
        })
        
        # Keep only the last 100 data points to avoid excessive storage
        if len(historical_data[symbol]) > 100:
            historical_data[symbol] = historical_data[symbol][-100:]
    
    # Save the updated historical data
    ctx.storage.set("historical_data", historical_data)
    ctx.logger.info(f"Updated historical data for {len(msg.prices)} symbols")
    
    # Perform analysis on each symbol and send results to user agent and alert agent
    analysis_results = []
    for symbol in msg.prices.keys():
        analysis_result = await analyze_price_data(ctx, symbol)
        
        if analysis_result:
            ctx.logger.info(f"Analysis for {symbol}: {analysis_result}")
            analysis_results.append(analysis_result)
            
            # Store the analysis result
            analysis_results_dict = ctx.storage.get("analysis_results")
            if analysis_results_dict is None:
                analysis_results_dict = {}
            analysis_results_dict[symbol] = analysis_result.dict()
            ctx.storage.set("analysis_results", analysis_results_dict)
            
            # Send the analysis result to alert agent
            alert_agent_address = os.getenv("ALERT_AGENT_ADDRESS")
            if alert_agent_address:
                ctx.logger.info(f"Sending analysis result for {symbol} to alert agent")
                await ctx.send(alert_agent_address, analysis_result)
    
    # If we have any analysis results and the request came from the user agent,
    # send them back to the user agent
    if analysis_results and sender == os.getenv("USER_AGENT_ADDRESS"):
        await ctx.send(sender, AnalysisResponse(results=analysis_results))


@analysis_protocol.on_message(model=AnalysisRequest, replies={AnalysisResponse})
async def handle_analysis_request(ctx: Context, sender: str, msg: AnalysisRequest):
    """
    Handle requests for technical analysis on a cryptocurrency.
    """
    ctx.logger.info(f"Received analysis request from {sender} for {msg.symbol}")
    
    # Perform analysis
    analysis_result = await analyze_price_data(ctx, msg.symbol)
    
    if analysis_result:
        # Send the analysis result
        await ctx.send(sender, AnalysisResponse(results=[analysis_result]))
    else:
        # Send an empty response
        await ctx.send(sender, AnalysisResponse(results=[]))


# Include the protocol in the agent
analysis_agent.include(analysis_protocol, publish_manifest=True)


if __name__ == "__main__":
    analysis_agent.run()

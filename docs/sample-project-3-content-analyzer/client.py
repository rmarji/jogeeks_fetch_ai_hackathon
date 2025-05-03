import os
import asyncio
from datetime import datetime, timedelta

from dotenv import load_dotenv
from uagents import Agent, Context

from models import (
    Platform,
    TimeFrame,
    FetchContentRequest,
    FetchContentResponse,
    FetchMetricsRequest,
    FetchMetricsResponse,
    GenerateReportRequest,
    GenerateReportResponse,
    GetInsightsRequest,
    GetInsightsResponse
)

# Load environment variables
load_dotenv()

# Client agent configuration
CLIENT_SEED = "content-analyzer-client-seed"
CLIENT_PORT = 8001
CLIENT_ENDPOINT = f"http://localhost:{CLIENT_PORT}/submit"

# Content analyzer agent address (this would be set after the content analyzer agent is running)
CONTENT_ANALYZER_ADDRESS = os.getenv("CONTENT_ANALYZER_ADDRESS", "")

# Create the client agent
client_agent = Agent(
    name="content-analyzer-client",
    seed=CLIENT_SEED,
    port=CLIENT_PORT,
    endpoint=CLIENT_ENDPOINT,
)


@client_agent.on_event("startup")
async def startup(ctx: Context):
    """
    Initialize the client agent on startup.
    """
    ctx.logger.info(f"Content Analyzer Client started with address: {client_agent.address}")
    
    if not CONTENT_ANALYZER_ADDRESS:
        ctx.logger.warning("Content analyzer agent address not configured. Set the CONTENT_ANALYZER_ADDRESS environment variable.")
        return
    
    # Request content from YouTube
    await request_content(ctx, [Platform.YOUTUBE])
    
    # Wait a bit for the response
    await asyncio.sleep(2)
    
    # Generate a weekly report
    await generate_report(ctx, TimeFrame.WEEK)
    
    # Wait a bit for the response
    await asyncio.sleep(2)
    
    # Request insights
    await get_insights(ctx)


async def request_content(ctx: Context, platforms: list[Platform], limit: int = 10):
    """
    Request content from the content analyzer agent.
    
    Args:
        ctx: Agent context
        platforms: List of platforms to fetch content from
        limit: Maximum number of content items to fetch per platform
    """
    if not CONTENT_ANALYZER_ADDRESS:
        ctx.logger.error("Content analyzer agent address not configured")
        return
    
    # Calculate date range (last 30 days)
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=30)
    
    # Format dates as ISO strings
    start_date_str = start_date.isoformat()
    end_date_str = end_date.isoformat()
    
    ctx.logger.info(f"Requesting content from {', '.join([p.value for p in platforms])}")
    
    try:
        # Send request to content analyzer agent
        await ctx.send(CONTENT_ANALYZER_ADDRESS, FetchContentRequest(
            platforms=platforms,
            start_date=start_date_str,
            end_date=end_date_str,
            limit=limit
        ))
    except Exception as e:
        ctx.logger.error(f"Error requesting content: {e}")


async def request_metrics(ctx: Context, content_ids: list[str]):
    """
    Request metrics from the content analyzer agent.
    
    Args:
        ctx: Agent context
        content_ids: List of content IDs to fetch metrics for
    """
    if not CONTENT_ANALYZER_ADDRESS:
        ctx.logger.error("Content analyzer agent address not configured")
        return
    
    ctx.logger.info(f"Requesting metrics for {len(content_ids)} content items")
    
    try:
        # Send request to content analyzer agent
        await ctx.send(CONTENT_ANALYZER_ADDRESS, FetchMetricsRequest(
            content_ids=content_ids
        ))
    except Exception as e:
        ctx.logger.error(f"Error requesting metrics: {e}")


async def generate_report(ctx: Context, time_frame: TimeFrame):
    """
    Request a report from the content analyzer agent.
    
    Args:
        ctx: Agent context
        time_frame: Time frame for the report
    """
    if not CONTENT_ANALYZER_ADDRESS:
        ctx.logger.error("Content analyzer agent address not configured")
        return
    
    ctx.logger.info(f"Requesting {time_frame.value} report")
    
    try:
        # Send request to content analyzer agent
        await ctx.send(CONTENT_ANALYZER_ADDRESS, GenerateReportRequest(
            time_frame=time_frame,
            platforms=[Platform.YOUTUBE, Platform.INSTAGRAM, Platform.TIKTOK],
            include_recommendations=True
        ))
    except Exception as e:
        ctx.logger.error(f"Error requesting report: {e}")


async def get_insights(ctx: Context, limit: int = 5):
    """
    Request insights from the content analyzer agent.
    
    Args:
        ctx: Agent context
        limit: Maximum number of insights to fetch
    """
    if not CONTENT_ANALYZER_ADDRESS:
        ctx.logger.error("Content analyzer agent address not configured")
        return
    
    ctx.logger.info(f"Requesting insights")
    
    try:
        # Send request to content analyzer agent
        await ctx.send(CONTENT_ANALYZER_ADDRESS, GetInsightsRequest(
            limit=limit
        ))
    except Exception as e:
        ctx.logger.error(f"Error requesting insights: {e}")


@client_agent.on_message(model=FetchContentResponse)
async def handle_content_response(ctx: Context, sender: str, msg: FetchContentResponse):
    """
    Handle content responses from the content analyzer agent.
    """
    ctx.logger.info(f"Received content response from {sender} with {msg.total_count} items")
    
    if msg.content_items:
        # Log the first few content items
        for item in msg.content_items[:3]:
            ctx.logger.info(f"Content item: {item.platform.value} - {item.content_type.value} - {item.title or item.id}")
        
        # Request metrics for the content items
        content_ids = [item.id for item in msg.content_items]
        await request_metrics(ctx, content_ids)


@client_agent.on_message(model=FetchMetricsResponse)
async def handle_metrics_response(ctx: Context, sender: str, msg: FetchMetricsResponse):
    """
    Handle metrics responses from the content analyzer agent.
    """
    ctx.logger.info(f"Received metrics response from {sender} with {len(msg.metrics)} items")
    
    if msg.metrics:
        # Log the first few metrics
        for content_id, metrics in list(msg.metrics.items())[:3]:
            ctx.logger.info(f"Metrics for {content_id}: Views: {metrics.views}, Likes: {metrics.likes}, Comments: {metrics.comments}")


@client_agent.on_message(model=GenerateReportResponse)
async def handle_report_response(ctx: Context, sender: str, msg: GenerateReportResponse):
    """
    Handle report responses from the content analyzer agent.
    """
    if not msg.report:
        ctx.logger.error("Received empty report response")
        return
    
    report = msg.report
    
    ctx.logger.info(f"Received {report.time_frame.value} report from {sender}")
    ctx.logger.info(f"Report period: {report.start_date} to {report.end_date}")
    ctx.logger.info(f"Total content items: {report.total_content_items}")
    
    # Log insights
    ctx.logger.info(f"Report contains {len(report.insights)} insights:")
    for i, insight in enumerate(report.insights[:3], 1):
        ctx.logger.info(f"Insight {i}: {insight.description}")
    
    # Log recommendations
    ctx.logger.info(f"Report contains {len(report.recommendations)} recommendations:")
    for i, recommendation in enumerate(report.recommendations[:3], 1):
        ctx.logger.info(f"Recommendation {i}: {recommendation}")


@client_agent.on_message(model=GetInsightsResponse)
async def handle_insights_response(ctx: Context, sender: str, msg: GetInsightsResponse):
    """
    Handle insights responses from the content analyzer agent.
    """
    ctx.logger.info(f"Received insights response from {sender} with {len(msg.insights)} insights")
    
    for i, insight in enumerate(msg.insights, 1):
        ctx.logger.info(f"Insight {i}: {insight.insight_type} - {insight.description} (Confidence: {insight.confidence:.2f})")


if __name__ == "__main__":
    client_agent.run()

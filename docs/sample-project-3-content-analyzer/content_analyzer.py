import os
import json
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any, Tuple

from dotenv import load_dotenv
from uagents import Agent, Context
from uagents.experimental.quota import QuotaProtocol, RateLimit

from models import (
    ContentItem, 
    ContentMetrics, 
    AudienceData, 
    Platform, 
    ContentType,
    TimeFrame,
    PerformanceInsight,
    PerformanceReport,
    FetchContentRequest,
    FetchContentResponse,
    FetchMetricsRequest,
    FetchMetricsResponse,
    GenerateReportRequest,
    GenerateReportResponse,
    GetInsightsRequest,
    GetInsightsResponse
)

from platform_connectors import (
    YouTubeConnector,
    InstagramConnector,
    TikTokConnector
)

from analysis import (
    MetricsAnalyzer,
    PatternAnalyzer,
    InsightGenerator
)

# Load environment variables
load_dotenv()

# Agent configuration
AGENT_SEED = os.getenv("AGENT_SEED", "content-analyzer-agent-seed")
AGENT_PORT = int(os.getenv("AGENT_PORT", "8000"))
AGENT_ENDPOINT = f"http://localhost:{AGENT_PORT}/submit"

# Default settings
DEFAULT_PLATFORMS = os.getenv("DEFAULT_PLATFORMS", "YOUTUBE,INSTAGRAM,TIKTOK").split(",")
DEFAULT_TIME_FRAME = TimeFrame(os.getenv("DEFAULT_TIME_FRAME", "WEEK"))
DEFAULT_REPORT_SCHEDULE = os.getenv("DEFAULT_REPORT_SCHEDULE", "WEEKLY")

# Create the agent
content_analyzer = Agent(
    name="content-analyzer",
    seed=AGENT_SEED,
    port=AGENT_PORT,
    endpoint=AGENT_ENDPOINT,
)

# Create a protocol with rate limiting
content_analyzer_protocol = QuotaProtocol(
    storage_reference=content_analyzer.storage,
    name="Content-Analyzer-Protocol",
    version="0.1.0",
    default_rate_limit=RateLimit(window_size_minutes=1, max_requests=10),
)


class ContentAnalyzerAgent:
    """
    Agent for analyzing content performance across multiple platforms.
    """
    
    def __init__(self, ctx: Context):
        """
        Initialize the content analyzer agent.
        
        Args:
            ctx: Agent context
        """
        self.ctx = ctx
        
        # Initialize platform connectors
        try:
            self.youtube_connector = YouTubeConnector()
            ctx.logger.info("YouTube connector initialized")
        except Exception as e:
            self.youtube_connector = None
            ctx.logger.error(f"Failed to initialize YouTube connector: {e}")
        
        try:
            self.instagram_connector = InstagramConnector()
            ctx.logger.info("Instagram connector initialized")
        except Exception as e:
            self.instagram_connector = None
            ctx.logger.error(f"Failed to initialize Instagram connector: {e}")
        
        try:
            self.tiktok_connector = TikTokConnector()
            ctx.logger.info("TikTok connector initialized")
        except Exception as e:
            self.tiktok_connector = None
            ctx.logger.error(f"Failed to initialize TikTok connector: {e}")
        
        # Initialize analyzers
        self.metrics_analyzer = MetricsAnalyzer()
        self.pattern_analyzer = PatternAnalyzer()
        self.insight_generator = InsightGenerator()
        
        # Initialize storage
        self._initialize_storage()
    
    def _initialize_storage(self):
        """
        Initialize storage for the agent.
        """
        # Initialize content items storage
        if not self.ctx.storage.get("content_items"):
            self.ctx.storage.set("content_items", {})
        
        # Initialize metrics storage
        if not self.ctx.storage.get("metrics"):
            self.ctx.storage.set("metrics", {})
        
        # Initialize audience data storage
        if not self.ctx.storage.get("audience_data"):
            self.ctx.storage.set("audience_data", {})
        
        # Initialize insights storage
        if not self.ctx.storage.get("insights"):
            self.ctx.storage.set("insights", [])
        
        # Initialize reports storage
        if not self.ctx.storage.get("reports"):
            self.ctx.storage.set("reports", [])
    
    async def fetch_content(self, platforms: List[Platform], 
                           start_date: Optional[str] = None, 
                           end_date: Optional[str] = None, 
                           limit: int = 10) -> List[ContentItem]:
        """
        Fetch content from specified platforms.
        
        Args:
            platforms: List of platforms to fetch content from
            start_date: Start date for content (ISO format)
            end_date: End date for content (ISO format)
            limit: Maximum number of content items to fetch per platform
            
        Returns:
            List of ContentItem objects
        """
        content_items = []
        
        # Fetch content from YouTube
        if Platform.YOUTUBE in platforms and self.youtube_connector:
            try:
                youtube_items = await self.youtube_connector.fetch_content(
                    start_date=start_date,
                    end_date=end_date,
                    limit=limit
                )
                content_items.extend(youtube_items)
                self.ctx.logger.info(f"Fetched {len(youtube_items)} items from YouTube")
            except Exception as e:
                self.ctx.logger.error(f"Error fetching YouTube content: {e}")
        
        # Fetch content from Instagram
        if Platform.INSTAGRAM in platforms and self.instagram_connector:
            try:
                instagram_items = await self.instagram_connector.fetch_content(
                    start_date=start_date,
                    end_date=end_date,
                    limit=limit
                )
                content_items.extend(instagram_items)
                self.ctx.logger.info(f"Fetched {len(instagram_items)} items from Instagram")
            except Exception as e:
                self.ctx.logger.error(f"Error fetching Instagram content: {e}")
        
        # Fetch content from TikTok
        if Platform.TIKTOK in platforms and self.tiktok_connector:
            try:
                tiktok_items = await self.tiktok_connector.fetch_content(
                    start_date=start_date,
                    end_date=end_date,
                    limit=limit
                )
                content_items.extend(tiktok_items)
                self.ctx.logger.info(f"Fetched {len(tiktok_items)} items from TikTok")
            except Exception as e:
                self.ctx.logger.error(f"Error fetching TikTok content: {e}")
        
        # Store content items
        content_items_dict = self.ctx.storage.get("content_items", {})
        
        for item in content_items:
            content_items_dict[item.id] = item.dict()
        
        self.ctx.storage.set("content_items", content_items_dict)
        
        return content_items
    
    async def fetch_metrics(self, content_ids: List[str], 
                           platforms: Optional[List[Platform]] = None) -> Dict[str, ContentMetrics]:
        """
        Fetch metrics for content items.
        
        Args:
            content_ids: List of content IDs to fetch metrics for
            platforms: Optional list of platforms to filter by
            
        Returns:
            Dictionary mapping content IDs to ContentMetrics objects
        """
        # Get content items
        content_items_dict = self.ctx.storage.get("content_items", {})
        content_items = {}
        
        for content_id in content_ids:
            if content_id in content_items_dict:
                item_dict = content_items_dict[content_id]
                content_items[content_id] = ContentItem(**item_dict)
        
        if not content_items:
            return {}
        
        # Group content IDs by platform
        platform_content_ids = {}
        
        for content_id, item in content_items.items():
            if platforms and item.platform not in platforms:
                continue
            
            if item.platform not in platform_content_ids:
                platform_content_ids[item.platform] = []
            
            platform_content_ids[item.platform].append(content_id)
        
        metrics = {}
        
        # Fetch metrics from YouTube
        if Platform.YOUTUBE in platform_content_ids and self.youtube_connector:
            try:
                youtube_metrics = await self.youtube_connector.fetch_metrics(
                    platform_content_ids[Platform.YOUTUBE]
                )
                metrics.update(youtube_metrics)
                self.ctx.logger.info(f"Fetched metrics for {len(youtube_metrics)} YouTube items")
            except Exception as e:
                self.ctx.logger.error(f"Error fetching YouTube metrics: {e}")
        
        # Fetch metrics from Instagram
        if Platform.INSTAGRAM in platform_content_ids and self.instagram_connector:
            try:
                instagram_metrics = await self.instagram_connector.fetch_metrics(
                    platform_content_ids[Platform.INSTAGRAM]
                )
                metrics.update(instagram_metrics)
                self.ctx.logger.info(f"Fetched metrics for {len(instagram_metrics)} Instagram items")
            except Exception as e:
                self.ctx.logger.error(f"Error fetching Instagram metrics: {e}")
        
        # Fetch metrics from TikTok
        if Platform.TIKTOK in platform_content_ids and self.tiktok_connector:
            try:
                tiktok_metrics = await self.tiktok_connector.fetch_metrics(
                    platform_content_ids[Platform.TIKTOK]
                )
                metrics.update(tiktok_metrics)
                self.ctx.logger.info(f"Fetched metrics for {len(tiktok_metrics)} TikTok items")
            except Exception as e:
                self.ctx.logger.error(f"Error fetching TikTok metrics: {e}")
        
        # Store metrics
        metrics_dict = self.ctx.storage.get("metrics", {})
        
        for content_id, metric in metrics.items():
            metrics_dict[content_id] = metric.dict()
        
        self.ctx.storage.set("metrics", metrics_dict)
        
        return metrics
    
    async def fetch_audience_data(self, platforms: List[Platform]) -> Dict[Platform, AudienceData]:
        """
        Fetch audience data from specified platforms.
        
        Args:
            platforms: List of platforms to fetch audience data from
            
        Returns:
            Dictionary mapping platforms to AudienceData objects
        """
        audience_data = {}
        
        # Fetch audience data from YouTube
        if Platform.YOUTUBE in platforms and self.youtube_connector:
            try:
                youtube_audience = await self.youtube_connector.fetch_audience_data()
                if youtube_audience:
                    audience_data[Platform.YOUTUBE] = youtube_audience
                    self.ctx.logger.info("Fetched YouTube audience data")
            except Exception as e:
                self.ctx.logger.error(f"Error fetching YouTube audience data: {e}")
        
        # Fetch audience data from Instagram
        if Platform.INSTAGRAM in platforms and self.instagram_connector:
            try:
                instagram_audience = await self.instagram_connector.fetch_audience_data()
                if instagram_audience:
                    audience_data[Platform.INSTAGRAM] = instagram_audience
                    self.ctx.logger.info("Fetched Instagram audience data")
            except Exception as e:
                self.ctx.logger.error(f"Error fetching Instagram audience data: {e}")
        
        # Fetch audience data from TikTok
        if Platform.TIKTOK in platforms and self.tiktok_connector:
            try:
                tiktok_audience = await self.tiktok_connector.fetch_audience_data()
                if tiktok_audience:
                    audience_data[Platform.TIKTOK] = tiktok_audience
                    self.ctx.logger.info("Fetched TikTok audience data")
            except Exception as e:
                self.ctx.logger.error(f"Error fetching TikTok audience data: {e}")
        
        # Store audience data
        audience_data_dict = self.ctx.storage.get("audience_data", {})
        
        for platform, data in audience_data.items():
            audience_data_dict[platform.value] = data.dict()
        
        self.ctx.storage.set("audience_data", audience_data_dict)
        
        return audience_data
    
    def analyze_content(self, content_items: List[ContentItem], 
                       metrics: Dict[str, ContentMetrics]) -> Tuple[List[PerformanceInsight], List[str]]:
        """
        Analyze content performance and generate insights and recommendations.
        
        Args:
            content_items: List of ContentItem objects
            metrics: Dictionary mapping content IDs to ContentMetrics objects
            
        Returns:
            Tuple of (insights, recommendations)
        """
        if not content_items or not metrics:
            return [], []
        
        insights = []
        
        # Convert metrics dictionary to list
        metrics_list = list(metrics.values())
        
        # Calculate average metrics
        avg_metrics = self.metrics_analyzer.calculate_average_metrics(metrics_list)
        
        # Calculate platform metrics
        platform_metrics = self.metrics_analyzer.calculate_platform_metrics(metrics_list)
        
        # Identify top performing content
        top_content_ids = self.metrics_analyzer.identify_top_performing_content(
            content_items, metrics, "engagement_rate", 5
        )
        
        # Calculate posting frequency
        posting_frequency = self.metrics_analyzer.calculate_posting_frequency(content_items)
        
        # Calculate best posting times
        best_posting_times = self.metrics_analyzer.calculate_best_posting_times(content_items, metrics)
        
        # Identify content type performance
        content_type_performance = self.pattern_analyzer.identify_content_type_performance(content_items, metrics)
        
        # Identify platform performance
        platform_performance = self.pattern_analyzer.identify_platform_performance(content_items, metrics)
        
        # Identify popular topics
        popular_topics = self.pattern_analyzer.identify_popular_topics(content_items, metrics)
        
        # Identify popular hashtags
        popular_hashtags = self.pattern_analyzer.identify_popular_hashtags(content_items, metrics)
        
        # Identify content length performance
        content_length_performance = self.pattern_analyzer.identify_content_length_performance(content_items, metrics)
        
        # Identify seasonal patterns
        seasonal_patterns = self.pattern_analyzer.identify_seasonal_patterns(content_items, metrics)
        
        # Generate insights
        if content_type_performance:
            insights.extend(self.insight_generator.generate_content_type_insights(content_type_performance))
        
        if platform_performance:
            insights.extend(self.insight_generator.generate_platform_insights(platform_performance))
        
        if popular_topics:
            insights.extend(self.insight_generator.generate_topic_insights(popular_topics))
        
        if popular_hashtags:
            insights.extend(self.insight_generator.generate_hashtag_insights(popular_hashtags))
        
        if content_length_performance:
            insights.extend(self.insight_generator.generate_content_length_insights(content_length_performance))
        
        if best_posting_times:
            insights.extend(self.insight_generator.generate_posting_time_insights(best_posting_times))
        
        if seasonal_patterns:
            insights.extend(self.insight_generator.generate_seasonal_insights(seasonal_patterns))
        
        # Store insights
        insights_dict = self.ctx.storage.get("insights", [])
        insights_dict.extend([insight.dict() for insight in insights])
        
        # Keep only the last 100 insights to avoid excessive storage
        if len(insights_dict) > 100:
            insights_dict = insights_dict[-100:]
        
        self.ctx.storage.set("insights", insights_dict)
        
        # Generate recommendations
        recommendations = self.insight_generator.generate_recommendations(insights)
        
        return insights, recommendations
    
    async def generate_report(self, time_frame: TimeFrame, 
                             platforms: Optional[List[Platform]] = None,
                             include_recommendations: bool = True) -> Optional[PerformanceReport]:
        """
        Generate a performance report for a time period.
        
        Args:
            time_frame: Time frame for the report
            platforms: Optional list of platforms to include in the report
            include_recommendations: Whether to include recommendations in the report
            
        Returns:
            PerformanceReport object or None if report generation fails
        """
        # Determine date range based on time frame
        end_date = datetime.utcnow()
        
        if time_frame == TimeFrame.DAY:
            start_date = end_date - timedelta(days=1)
        elif time_frame == TimeFrame.WEEK:
            start_date = end_date - timedelta(days=7)
        elif time_frame == TimeFrame.MONTH:
            start_date = end_date - timedelta(days=30)
        elif time_frame == TimeFrame.QUARTER:
            start_date = end_date - timedelta(days=90)
        elif time_frame == TimeFrame.YEAR:
            start_date = end_date - timedelta(days=365)
        else:  # ALL_TIME
            start_date = datetime(2000, 1, 1)  # A long time ago
        
        # Format dates as ISO strings
        start_date_str = start_date.isoformat()
        end_date_str = end_date.isoformat()
        
        # Use default platforms if not specified
        if not platforms:
            platforms = [Platform(p) for p in DEFAULT_PLATFORMS if hasattr(Platform, p)]
        
        # Fetch content for the time period
        content_items = await self.fetch_content(
            platforms=platforms,
            start_date=start_date_str,
            end_date=end_date_str,
            limit=100
        )
        
        if not content_items:
            self.ctx.logger.error("No content items found for the specified time period")
            return None
        
        # Fetch metrics for the content items
        content_ids = [item.id for item in content_items]
        metrics = await self.fetch_metrics(content_ids, platforms)
        
        if not metrics:
            self.ctx.logger.error("No metrics found for the content items")
            return None
        
        # Analyze content and generate insights and recommendations
        insights, recommendations = self.analyze_content(content_items, metrics)
        
        # Identify top performing content
        top_content_ids = self.metrics_analyzer.identify_top_performing_content(
            content_items, metrics, "engagement_rate", 5
        )
        
        # Convert metrics dictionary to list
        metrics_list = list(metrics.values())
        
        # Calculate average metrics
        avg_metrics = self.metrics_analyzer.calculate_average_metrics(metrics_list)
        
        # Calculate platform metrics
        platform_metrics = self.metrics_analyzer.calculate_platform_metrics(metrics_list)
        
        # Create metrics summary
        metrics_summary = {
            "average_metrics": avg_metrics,
            "platform_metrics": {p.value: m for p, m in platform_metrics.items()},
            "total_views": sum(m.views or 0 for m in metrics_list),
            "total_likes": sum(m.likes or 0 for m in metrics_list),
            "total_comments": sum(m.comments or 0 for m in metrics_list),
            "total_shares": sum(m.shares or 0 for m in metrics_list)
        }
        
        # Create the report
        report = PerformanceReport.create(
            time_frame=time_frame,
            start_date=start_date_str,
            end_date=end_date_str,
            platforms=platforms,
            total_content_items=len(content_items),
            top_performing_content=top_content_ids,
            metrics_summary=metrics_summary,
            insights=insights,
            recommendations=recommendations if include_recommendations else []
        )
        
        # Store the report
        reports = self.ctx.storage.get("reports", [])
        reports.append(report.dict())
        
        # Keep only the last 10 reports to avoid excessive storage
        if len(reports) > 10:
            reports = reports[-10:]
        
        self.ctx.storage.set("reports", reports)
        
        return report


@content_analyzer.on_event("startup")
async def startup(ctx: Context):
    """
    Initialize the content analyzer agent on startup.
    """
    ctx.logger.info(f"Content Analyzer Agent started with address: {content_analyzer.address}")
    
    # Create the agent instance
    agent = ContentAnalyzerAgent(ctx)
    
    # Store the agent instance
    ctx.storage.set("agent_instance", agent)
    
    # Schedule the first report generation
    if DEFAULT_REPORT_SCHEDULE == "DAILY":
        ctx.logger.info("Scheduling daily report generation")
        asyncio.create_task(schedule_daily_report(ctx))
    elif DEFAULT_REPORT_SCHEDULE == "WEEKLY":
        ctx.logger.info("Scheduling weekly report generation")
        asyncio.create_task(schedule_weekly_report(ctx))
    elif DEFAULT_REPORT_SCHEDULE == "MONTHLY":
        ctx.logger.info("Scheduling monthly report generation")
        asyncio.create_task(schedule_monthly_report(ctx))


async def schedule_daily_report(ctx: Context):
    """
    Schedule daily report generation.
    """
    while True:
        # Wait until the next day at 00:00
        now = datetime.utcnow()
        tomorrow = now.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
        wait_seconds = (tomorrow - now).total_seconds()
        
        await asyncio.sleep(wait_seconds)
        
        # Generate the report
        await generate_scheduled_report(ctx, TimeFrame.DAY)


async def schedule_weekly_report(ctx: Context):
    """
    Schedule weekly report generation.
    """
    while True:
        # Wait until the next Monday at 00:00
        now = datetime.utcnow()
        days_until_monday = (7 - now.weekday()) % 7
        next_monday = now.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=days_until_monday)
        wait_seconds = (next_monday - now).total_seconds()
        
        await asyncio.sleep(wait_seconds)
        
        # Generate the report
        await generate_scheduled_report(ctx, TimeFrame.WEEK)


async def schedule_monthly_report(ctx: Context):
    """
    Schedule monthly report generation.
    """
    while True:
        # Wait until the first day of the next month at 00:00
        now = datetime.utcnow()
        if now.month == 12:
            next_month = now.replace(year=now.year + 1, month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        else:
            next_month = now.replace(month=now.month + 1, day=1, hour=0, minute=0, second=0, microsecond=0)
        
        wait_seconds = (next_month - now).total_seconds()
        
        await asyncio.sleep(wait_seconds)
        
        # Generate the report
        await generate_scheduled_report(ctx, TimeFrame.MONTH)


async def generate_scheduled_report(ctx: Context, time_frame: TimeFrame):
    """
    Generate a scheduled report.
    
    Args:
        ctx: Agent context
        time_frame: Time frame for the report
    """
    ctx.logger.info(f"Generating scheduled {time_frame.value} report")
    
    # Get the agent instance
    agent = ctx.storage.get("agent_instance")
    
    if not agent:
        ctx.logger.error("Agent instance not found")
        return
    
    # Generate the report
    report = await agent.generate_report(
        time_frame=time_frame,
        platforms=[Platform(p) for p in DEFAULT_PLATFORMS if hasattr(Platform, p)],
        include_recommendations=True
    )
    
    if report:
        ctx.logger.info(f"Generated {time_frame.value} report with {len(report.insights)} insights and {len(report.recommendations)} recommendations")
    else:
        ctx.logger.error(f"Failed to generate {time_frame.value} report")


@content_analyzer_protocol.on_message(model=FetchContentRequest, replies={FetchContentResponse})
async def handle_fetch_content(ctx: Context, sender: str, msg: FetchContentRequest):
    """
    Handle requests to fetch content.
    """
    ctx.logger.info(f"Received request to fetch content from {sender}")
    
    # Get the agent instance
    agent = ctx.storage.get("agent_instance")
    
    if not agent:
        ctx.logger.error("Agent instance not found")
        await ctx.send(sender, FetchContentResponse(content_items=[], total_count=0))
        return
    
    # Fetch content
    content_items = await agent.fetch_content(
        platforms=msg.platforms,
        start_date=msg.start_date,
        end_date=msg.end_date,
        limit=msg.limit
    )
    
    # Send response
    await ctx.send(sender, FetchContentResponse(
        content_items=content_items,
        total_count=len(content_items)
    ))


@content_analyzer_protocol.on_message(model=FetchMetricsRequest, replies={FetchMetricsResponse})
async def handle_fetch_metrics(ctx: Context, sender: str, msg: FetchMetricsRequest):
    """
    Handle requests to fetch metrics.
    """
    ctx.logger.info(f"Received request to fetch metrics from {sender}")
    
    # Get the agent instance
    agent = ctx.storage.get("agent_instance")
    
    if not agent:
        ctx.logger.error("Agent instance not found")
        await ctx.send(sender, FetchMetricsResponse(metrics={}))
        return
    
    # Fetch metrics
    metrics = await agent.fetch_metrics(
        content_ids=msg.content_ids,
        platforms=msg.platforms
    )
    
    # Send response
    await ctx.send(sender, FetchMetricsResponse(metrics=metrics))


@content_analyzer_protocol.on_message(model=GenerateReportRequest, replies={GenerateReportResponse})
async def handle_generate_report(ctx: Context, sender: str, msg: GenerateReportRequest):
    """
    Handle requests to generate a report.
    """
    ctx.logger.info(f"Received request to generate a report from {sender}")
    
    # Get the agent instance
    agent = ctx.storage.get("agent_instance")
    
    if not agent:
        ctx.logger.error("Agent instance not found")
        await ctx.send(sender, GenerateReportResponse(report=None))
        return
    
    # Generate the report
    report = await agent.generate_report(
        time_frame=msg.time_frame,
        platforms=msg.platforms,
        include_recommendations=msg.include_recommendations
    )
    
    # Send response
    await ctx.send(sender, GenerateReportResponse(report=report))


@content_analyzer_protocol.on_message(model=GetInsightsRequest, replies={GetInsightsResponse})
async def handle_get_insights(ctx: Context, sender: str, msg: GetInsightsRequest):
    """
    Handle requests to get insights.
    """
    ctx.logger.info(f"Received request to get insights from {sender}")
    
    # Get insights from storage
    insights_dict = ctx.storage.get("insights", [])
    
    # Convert dictionaries to PerformanceInsight objects
    insights = [PerformanceInsight(**insight) for insight in insights_dict]
    
    # Filter insights if requested
    if msg.content_id:
        insights = [insight for insight in insights if insight.content_id == msg.content_id]
    
    if msg.platform:
        insights = [insight for insight in insights if insight.platform == msg.platform]
    
    # Limit the number of insights
    insights = insights[:msg.limit]
    
    # Send response
    await ctx.send(sender, GetInsightsResponse(insights=insights))


# Include the protocol in the agent
content_analyzer.include(content_analyzer_protocol, publish_manifest=True)


if __name__ == "__main__":
    content_analyzer.run()

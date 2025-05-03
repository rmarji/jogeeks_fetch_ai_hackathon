from enum import Enum
from typing import List, Dict, Optional, Any
from datetime import datetime
from uagents import Model


class Platform(str, Enum):
    """
    Enum representing different social media platforms.
    """
    YOUTUBE = "youtube"
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    TWITTER = "twitter"
    FACEBOOK = "facebook"


class ContentType(str, Enum):
    """
    Enum representing different types of content.
    """
    VIDEO = "video"
    IMAGE = "image"
    TEXT = "text"
    STORY = "story"
    REEL = "reel"
    LIVE = "live"


class TimeFrame(str, Enum):
    """
    Enum representing different time frames for analysis.
    """
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    QUARTER = "quarter"
    YEAR = "year"
    ALL_TIME = "all_time"


class ContentItem(Model):
    """
    Model representing a content item from any platform.
    """
    id: str
    platform: Platform
    content_type: ContentType
    title: Optional[str] = None
    description: Optional[str] = None
    url: str
    published_at: str
    tags: Optional[List[str]] = None
    
    def __str__(self):
        return f"{self.platform.value.capitalize()} {self.content_type.value}: {self.title or self.id}"


class ContentMetrics(Model):
    """
    Model representing metrics for a content item.
    """
    content_id: str
    platform: Platform
    timestamp: str
    views: Optional[int] = None
    likes: Optional[int] = None
    comments: Optional[int] = None
    shares: Optional[int] = None
    saves: Optional[int] = None
    watch_time: Optional[int] = None  # In seconds
    average_view_duration: Optional[float] = None  # In seconds
    click_through_rate: Optional[float] = None  # As a percentage
    engagement_rate: Optional[float] = None  # As a percentage
    additional_metrics: Optional[Dict[str, Any]] = None
    
    @classmethod
    def create(cls, content_id: str, platform: Platform, **metrics):
        """
        Factory method to create ContentMetrics with the current timestamp.
        """
        return cls(
            content_id=content_id,
            platform=platform,
            timestamp=datetime.utcnow().isoformat(),
            **metrics
        )


class AudienceData(Model):
    """
    Model representing audience data for a content item or channel.
    """
    platform: Platform
    timestamp: str
    total_followers: Optional[int] = None
    age_distribution: Optional[Dict[str, float]] = None  # Age range -> percentage
    gender_distribution: Optional[Dict[str, float]] = None  # Gender -> percentage
    location_distribution: Optional[Dict[str, float]] = None  # Country/region -> percentage
    device_distribution: Optional[Dict[str, float]] = None  # Device type -> percentage
    
    @classmethod
    def create(cls, platform: Platform, **data):
        """
        Factory method to create AudienceData with the current timestamp.
        """
        return cls(
            platform=platform,
            timestamp=datetime.utcnow().isoformat(),
            **data
        )


class PerformanceInsight(Model):
    """
    Model representing an insight derived from content performance analysis.
    """
    content_id: Optional[str] = None  # If specific to a content item
    platform: Optional[Platform] = None  # If specific to a platform
    insight_type: str  # E.g., "trend", "recommendation", "observation"
    description: str
    confidence: float  # 0.0 to 1.0
    supporting_data: Optional[Dict[str, Any]] = None
    timestamp: str
    
    @classmethod
    def create(cls, insight_type: str, description: str, confidence: float, **kwargs):
        """
        Factory method to create a PerformanceInsight with the current timestamp.
        """
        return cls(
            insight_type=insight_type,
            description=description,
            confidence=confidence,
            timestamp=datetime.utcnow().isoformat(),
            **kwargs
        )


class PerformanceReport(Model):
    """
    Model representing a performance report for a time period.
    """
    time_frame: TimeFrame
    start_date: str
    end_date: str
    platforms: List[Platform]
    total_content_items: int
    top_performing_content: List[str]  # Content IDs
    metrics_summary: Dict[str, Any]
    insights: List[PerformanceInsight]
    recommendations: List[str]
    timestamp: str
    
    @classmethod
    def create(cls, time_frame: TimeFrame, start_date: str, end_date: str, 
               platforms: List[Platform], total_content_items: int, 
               top_performing_content: List[str], metrics_summary: Dict[str, Any],
               insights: List[PerformanceInsight], recommendations: List[str]):
        """
        Factory method to create a PerformanceReport with the current timestamp.
        """
        return cls(
            time_frame=time_frame,
            start_date=start_date,
            end_date=end_date,
            platforms=platforms,
            total_content_items=total_content_items,
            top_performing_content=top_performing_content,
            metrics_summary=metrics_summary,
            insights=insights,
            recommendations=recommendations,
            timestamp=datetime.utcnow().isoformat()
        )


# Request/Response models for the agent API

class FetchContentRequest(Model):
    """
    Request model for fetching content items.
    """
    platforms: List[Platform]
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    limit: int = 10


class FetchContentResponse(Model):
    """
    Response model for fetching content items.
    """
    content_items: List[ContentItem]
    total_count: int


class FetchMetricsRequest(Model):
    """
    Request model for fetching metrics for content items.
    """
    content_ids: List[str]
    platforms: Optional[List[Platform]] = None


class FetchMetricsResponse(Model):
    """
    Response model for fetching metrics for content items.
    """
    metrics: Dict[str, ContentMetrics]  # Content ID -> Metrics


class GenerateReportRequest(Model):
    """
    Request model for generating a performance report.
    """
    time_frame: TimeFrame
    platforms: Optional[List[Platform]] = None
    include_recommendations: bool = True


class GenerateReportResponse(Model):
    """
    Response model for generating a performance report.
    """
    report: PerformanceReport


class GetInsightsRequest(Model):
    """
    Request model for getting insights.
    """
    content_id: Optional[str] = None
    platform: Optional[Platform] = None
    limit: int = 5


class GetInsightsResponse(Model):
    """
    Response model for getting insights.
    """
    insights: List[PerformanceInsight]

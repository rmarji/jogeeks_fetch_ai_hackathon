import os
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
import googleapiclient.discovery
from googleapiclient.errors import HttpError

from models import ContentItem, ContentMetrics, AudienceData, Platform, ContentType


class YouTubeConnector:
    """
    Connector for the YouTube API to fetch content and metrics.
    """
    
    def __init__(self, api_key: Optional[str] = None, channel_id: Optional[str] = None):
        """
        Initialize the YouTube connector.
        
        Args:
            api_key: YouTube API key (defaults to environment variable)
            channel_id: YouTube channel ID (defaults to environment variable)
        """
        self.api_key = api_key or os.getenv("YOUTUBE_API_KEY")
        self.channel_id = channel_id or os.getenv("YOUTUBE_CHANNEL_ID")
        
        if not self.api_key:
            raise ValueError("YouTube API key not provided")
        
        if not self.channel_id:
            raise ValueError("YouTube channel ID not provided")
        
        # Initialize the YouTube API client
        self.youtube = googleapiclient.discovery.build(
            "youtube", "v3", developerKey=self.api_key
        )
    
    async def fetch_content(self, start_date: Optional[str] = None, 
                           end_date: Optional[str] = None, 
                           limit: int = 10) -> List[ContentItem]:
        """
        Fetch YouTube videos for the configured channel.
        
        Args:
            start_date: Start date for content (ISO format)
            end_date: End date for content (ISO format)
            limit: Maximum number of videos to fetch
            
        Returns:
            List of ContentItem objects
        """
        try:
            # Convert dates to datetime objects if provided
            start_datetime = datetime.fromisoformat(start_date) if start_date else None
            end_datetime = datetime.fromisoformat(end_date) if end_date else None
            
            # Get uploads playlist ID for the channel
            channels_response = self.youtube.channels().list(
                part="contentDetails",
                id=self.channel_id
            ).execute()
            
            if not channels_response["items"]:
                raise ValueError(f"Channel not found: {self.channel_id}")
            
            uploads_playlist_id = channels_response["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
            
            # Get videos from the uploads playlist
            playlist_items_response = self.youtube.playlistItems().list(
                part="snippet,contentDetails",
                playlistId=uploads_playlist_id,
                maxResults=limit
            ).execute()
            
            content_items = []
            
            for item in playlist_items_response["items"]:
                video_id = item["contentDetails"]["videoId"]
                published_at = item["snippet"]["publishedAt"]
                published_datetime = datetime.fromisoformat(published_at.replace("Z", "+00:00"))
                
                # Filter by date if provided
                if start_datetime and published_datetime < start_datetime:
                    continue
                if end_datetime and published_datetime > end_datetime:
                    continue
                
                # Get video details
                video_response = self.youtube.videos().list(
                    part="snippet,contentDetails",
                    id=video_id
                ).execute()
                
                if not video_response["items"]:
                    continue
                
                video = video_response["items"][0]
                
                # Extract tags
                tags = video["snippet"].get("tags", [])
                
                # Create ContentItem
                content_item = ContentItem(
                    id=video_id,
                    platform=Platform.YOUTUBE,
                    content_type=ContentType.VIDEO,
                    title=video["snippet"]["title"],
                    description=video["snippet"]["description"],
                    url=f"https://www.youtube.com/watch?v={video_id}",
                    published_at=published_at,
                    tags=tags
                )
                
                content_items.append(content_item)
                
                # Stop if we've reached the limit
                if len(content_items) >= limit:
                    break
            
            return content_items
        
        except HttpError as e:
            print(f"YouTube API error: {e}")
            return []
        except Exception as e:
            print(f"Error fetching YouTube content: {e}")
            return []
    
    async def fetch_metrics(self, content_ids: List[str]) -> Dict[str, ContentMetrics]:
        """
        Fetch metrics for YouTube videos.
        
        Args:
            content_ids: List of YouTube video IDs
            
        Returns:
            Dictionary mapping video IDs to ContentMetrics objects
        """
        try:
            metrics = {}
            
            # Fetch metrics for each video
            for video_id in content_ids:
                # Get video statistics
                video_response = self.youtube.videos().list(
                    part="statistics",
                    id=video_id
                ).execute()
                
                if not video_response["items"]:
                    continue
                
                stats = video_response["items"][0]["statistics"]
                
                # Create ContentMetrics
                metrics[video_id] = ContentMetrics.create(
                    content_id=video_id,
                    platform=Platform.YOUTUBE,
                    views=int(stats.get("viewCount", 0)),
                    likes=int(stats.get("likeCount", 0)),
                    comments=int(stats.get("commentCount", 0)),
                    # YouTube API doesn't provide shares or saves directly
                    engagement_rate=self._calculate_engagement_rate(stats)
                )
            
            return metrics
        
        except HttpError as e:
            print(f"YouTube API error: {e}")
            return {}
        except Exception as e:
            print(f"Error fetching YouTube metrics: {e}")
            return {}
    
    async def fetch_audience_data(self) -> Optional[AudienceData]:
        """
        Fetch audience data for the YouTube channel.
        
        Returns:
            AudienceData object or None if data cannot be fetched
        """
        try:
            # Note: Detailed audience demographics require YouTube Analytics API
            # and OAuth 2.0 authentication, which is beyond the scope of this example.
            # Here we're just fetching basic channel statistics.
            
            channel_response = self.youtube.channels().list(
                part="statistics",
                id=self.channel_id
            ).execute()
            
            if not channel_response["items"]:
                return None
            
            stats = channel_response["items"][0]["statistics"]
            
            # Create AudienceData
            audience_data = AudienceData.create(
                platform=Platform.YOUTUBE,
                total_followers=int(stats.get("subscriberCount", 0))
            )
            
            return audience_data
        
        except HttpError as e:
            print(f"YouTube API error: {e}")
            return None
        except Exception as e:
            print(f"Error fetching YouTube audience data: {e}")
            return None
    
    def _calculate_engagement_rate(self, stats: Dict[str, str]) -> float:
        """
        Calculate engagement rate for a YouTube video.
        
        Engagement rate = (likes + comments) / views * 100
        
        Args:
            stats: Video statistics from the YouTube API
            
        Returns:
            Engagement rate as a percentage
        """
        views = int(stats.get("viewCount", 0))
        likes = int(stats.get("likeCount", 0))
        comments = int(stats.get("commentCount", 0))
        
        if views == 0:
            return 0.0
        
        return (likes + comments) / views * 100

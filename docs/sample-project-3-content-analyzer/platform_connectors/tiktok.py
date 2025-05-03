import os
import requests
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta

from models import ContentItem, ContentMetrics, AudienceData, Platform, ContentType


class TikTokConnector:
    """
    Connector for the TikTok API to fetch content and metrics.
    
    Note: This is a simplified implementation using the TikTok for Developers API.
    In a real-world scenario, you would need to handle authentication flows,
    token refreshing, and more comprehensive error handling.
    """
    
    def __init__(self, access_token: Optional[str] = None, open_id: Optional[str] = None):
        """
        Initialize the TikTok connector.
        
        Args:
            access_token: TikTok access token (defaults to environment variable)
            open_id: TikTok open ID (defaults to environment variable)
        """
        self.access_token = access_token or os.getenv("TIKTOK_ACCESS_TOKEN")
        self.open_id = open_id or os.getenv("TIKTOK_OPEN_ID")
        
        if not self.access_token:
            raise ValueError("TikTok access token not provided")
        
        if not self.open_id:
            raise ValueError("TikTok open ID not provided")
        
        self.api_base_url = "https://open.tiktokapis.com/v2"
    
    async def fetch_content(self, start_date: Optional[str] = None, 
                           end_date: Optional[str] = None, 
                           limit: int = 10) -> List[ContentItem]:
        """
        Fetch TikTok videos for the configured user.
        
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
            
            # Get videos for the user
            url = f"{self.api_base_url}/video/list/"
            headers = {
                "Authorization": f"Bearer {self.access_token}"
            }
            params = {
                "fields": "id,create_time,share_url,title,video_description,duration,height,width,cover_image_url,share_count,comment_count,like_count,view_count",
                "max_count": limit
            }
            
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            if "data" not in data or "videos" not in data["data"]:
                return []
            
            content_items = []
            
            for video in data["data"]["videos"]:
                video_id = video["id"]
                published_at = video["create_time"]
                published_datetime = datetime.fromisoformat(published_at.replace("Z", "+00:00"))
                
                # Filter by date if provided
                if start_datetime and published_datetime < start_datetime:
                    continue
                if end_datetime and published_datetime > end_datetime:
                    continue
                
                # Create ContentItem
                content_item = ContentItem(
                    id=video_id,
                    platform=Platform.TIKTOK,
                    content_type=ContentType.VIDEO,
                    title=video.get("title", ""),
                    description=video.get("video_description", ""),
                    url=video["share_url"],
                    published_at=published_at,
                    tags=self._extract_hashtags(video.get("video_description", ""))
                )
                
                content_items.append(content_item)
                
                # Stop if we've reached the limit
                if len(content_items) >= limit:
                    break
            
            return content_items
        
        except requests.exceptions.RequestException as e:
            print(f"TikTok API error: {e}")
            return []
        except Exception as e:
            print(f"Error fetching TikTok content: {e}")
            return []
    
    async def fetch_metrics(self, content_ids: List[str]) -> Dict[str, ContentMetrics]:
        """
        Fetch metrics for TikTok videos.
        
        Args:
            content_ids: List of TikTok video IDs
            
        Returns:
            Dictionary mapping video IDs to ContentMetrics objects
        """
        try:
            metrics = {}
            
            # Fetch metrics for each video
            for video_id in content_ids:
                # Get video data
                url = f"{self.api_base_url}/video/query/"
                headers = {
                    "Authorization": f"Bearer {self.access_token}"
                }
                params = {
                    "fields": "id,share_count,comment_count,like_count,view_count",
                    "video_ids": [video_id]
                }
                
                response = requests.get(url, headers=headers, params=params)
                response.raise_for_status()
                
                data = response.json()
                
                if "data" not in data or "videos" not in data["data"] or not data["data"]["videos"]:
                    continue
                
                video = data["data"]["videos"][0]
                
                # Create ContentMetrics
                metrics[video_id] = ContentMetrics.create(
                    content_id=video_id,
                    platform=Platform.TIKTOK,
                    views=video.get("view_count", 0),
                    likes=video.get("like_count", 0),
                    comments=video.get("comment_count", 0),
                    shares=video.get("share_count", 0),
                    engagement_rate=self._calculate_engagement_rate(video)
                )
            
            return metrics
        
        except requests.exceptions.RequestException as e:
            print(f"TikTok API error: {e}")
            return {}
        except Exception as e:
            print(f"Error fetching TikTok metrics: {e}")
            return {}
    
    async def fetch_audience_data(self) -> Optional[AudienceData]:
        """
        Fetch audience data for the TikTok account.
        
        Returns:
            AudienceData object or None if data cannot be fetched
        """
        try:
            # Get user info
            url = f"{self.api_base_url}/user/info/"
            headers = {
                "Authorization": f"Bearer {self.access_token}"
            }
            params = {
                "fields": "open_id,union_id,avatar_url,avatar_url_100,avatar_large_url,display_name,bio_description,profile_deep_link,is_verified,follower_count,following_count,likes_count,video_count"
            }
            
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            if "data" not in data or "user" not in data["data"]:
                return None
            
            user = data["data"]["user"]
            
            # Create AudienceData
            audience_data = AudienceData.create(
                platform=Platform.TIKTOK,
                total_followers=user.get("follower_count", 0)
            )
            
            return audience_data
        
        except requests.exceptions.RequestException as e:
            print(f"TikTok API error: {e}")
            return None
        except Exception as e:
            print(f"Error fetching TikTok audience data: {e}")
            return None
    
    def _extract_hashtags(self, description: str) -> List[str]:
        """
        Extract hashtags from a TikTok video description.
        
        Args:
            description: TikTok video description
            
        Returns:
            List of hashtags
        """
        if not description:
            return []
        
        # Split by spaces and filter for hashtags
        words = description.split()
        hashtags = [word[1:] for word in words if word.startswith("#")]
        
        return hashtags
    
    def _calculate_engagement_rate(self, video: Dict[str, Any]) -> float:
        """
        Calculate engagement rate for a TikTok video.
        
        Engagement rate = (likes + comments + shares) / views * 100
        
        Args:
            video: Video data from the TikTok API
            
        Returns:
            Engagement rate as a percentage
        """
        views = video.get("view_count", 0)
        likes = video.get("like_count", 0)
        comments = video.get("comment_count", 0)
        shares = video.get("share_count", 0)
        
        if views == 0:
            return 0.0
        
        return (likes + comments + shares) / views * 100

import os
import requests
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta

from models import ContentItem, ContentMetrics, AudienceData, Platform, ContentType


class InstagramConnector:
    """
    Connector for the Instagram API to fetch content and metrics.
    
    Note: This is a simplified implementation using the Instagram Graph API.
    In a real-world scenario, you would need to handle authentication flows,
    token refreshing, and more comprehensive error handling.
    """
    
    def __init__(self, access_token: Optional[str] = None, user_id: Optional[str] = None):
        """
        Initialize the Instagram connector.
        
        Args:
            access_token: Instagram access token (defaults to environment variable)
            user_id: Instagram user ID (defaults to environment variable)
        """
        self.access_token = access_token or os.getenv("INSTAGRAM_ACCESS_TOKEN")
        self.user_id = user_id or os.getenv("INSTAGRAM_USER_ID")
        
        if not self.access_token:
            raise ValueError("Instagram access token not provided")
        
        if not self.user_id:
            raise ValueError("Instagram user ID not provided")
        
        self.api_base_url = "https://graph.instagram.com/v18.0"
    
    async def fetch_content(self, start_date: Optional[str] = None, 
                           end_date: Optional[str] = None, 
                           limit: int = 10) -> List[ContentItem]:
        """
        Fetch Instagram posts for the configured user.
        
        Args:
            start_date: Start date for content (ISO format)
            end_date: End date for content (ISO format)
            limit: Maximum number of posts to fetch
            
        Returns:
            List of ContentItem objects
        """
        try:
            # Convert dates to datetime objects if provided
            start_datetime = datetime.fromisoformat(start_date) if start_date else None
            end_datetime = datetime.fromisoformat(end_date) if end_date else None
            
            # Get media for the user
            url = f"{self.api_base_url}/{self.user_id}/media"
            params = {
                "access_token": self.access_token,
                "fields": "id,caption,media_type,media_url,permalink,timestamp,thumbnail_url",
                "limit": limit
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            if "data" not in data:
                return []
            
            content_items = []
            
            for item in data["data"]:
                media_id = item["id"]
                published_at = item["timestamp"]
                published_datetime = datetime.fromisoformat(published_at.replace("Z", "+00:00"))
                
                # Filter by date if provided
                if start_datetime and published_datetime < start_datetime:
                    continue
                if end_datetime and published_datetime > end_datetime:
                    continue
                
                # Determine content type
                media_type = item["media_type"].lower()
                if media_type == "image":
                    content_type = ContentType.IMAGE
                elif media_type == "video":
                    content_type = ContentType.VIDEO
                elif media_type == "carousel_album":
                    # For simplicity, we'll treat carousel albums as images
                    content_type = ContentType.IMAGE
                else:
                    content_type = ContentType.IMAGE
                
                # Create ContentItem
                content_item = ContentItem(
                    id=media_id,
                    platform=Platform.INSTAGRAM,
                    content_type=content_type,
                    title=None,  # Instagram posts don't have titles
                    description=item.get("caption", ""),
                    url=item["permalink"],
                    published_at=published_at,
                    tags=self._extract_hashtags(item.get("caption", ""))
                )
                
                content_items.append(content_item)
                
                # Stop if we've reached the limit
                if len(content_items) >= limit:
                    break
            
            return content_items
        
        except requests.exceptions.RequestException as e:
            print(f"Instagram API error: {e}")
            return []
        except Exception as e:
            print(f"Error fetching Instagram content: {e}")
            return []
    
    async def fetch_metrics(self, content_ids: List[str]) -> Dict[str, ContentMetrics]:
        """
        Fetch metrics for Instagram posts.
        
        Args:
            content_ids: List of Instagram media IDs
            
        Returns:
            Dictionary mapping media IDs to ContentMetrics objects
        """
        try:
            metrics = {}
            
            # Fetch metrics for each post
            for media_id in content_ids:
                # Get media insights
                url = f"{self.api_base_url}/{media_id}/insights"
                params = {
                    "access_token": self.access_token,
                    "metric": "engagement,impressions,reach,saved"
                }
                
                response = requests.get(url, params=params)
                response.raise_for_status()
                
                data = response.json()
                
                if "data" not in data:
                    continue
                
                # Extract metrics
                insights = {item["name"]: item["values"][0]["value"] for item in data["data"]}
                
                # Get comments and likes
                url = f"{self.api_base_url}/{media_id}"
                params = {
                    "access_token": self.access_token,
                    "fields": "comments_count,like_count"
                }
                
                response = requests.get(url, params=params)
                response.raise_for_status()
                
                media_data = response.json()
                
                # Create ContentMetrics
                metrics[media_id] = ContentMetrics.create(
                    content_id=media_id,
                    platform=Platform.INSTAGRAM,
                    views=insights.get("impressions", 0),
                    likes=media_data.get("like_count", 0),
                    comments=media_data.get("comments_count", 0),
                    saves=insights.get("saved", 0),
                    engagement_rate=self._calculate_engagement_rate(
                        insights.get("engagement", 0),
                        insights.get("impressions", 0)
                    )
                )
            
            return metrics
        
        except requests.exceptions.RequestException as e:
            print(f"Instagram API error: {e}")
            return {}
        except Exception as e:
            print(f"Error fetching Instagram metrics: {e}")
            return {}
    
    async def fetch_audience_data(self) -> Optional[AudienceData]:
        """
        Fetch audience data for the Instagram account.
        
        Returns:
            AudienceData object or None if data cannot be fetched
        """
        try:
            # Get user account info
            url = f"{self.api_base_url}/{self.user_id}"
            params = {
                "access_token": self.access_token,
                "fields": "followers_count,media_count"
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            # Create AudienceData
            audience_data = AudienceData.create(
                platform=Platform.INSTAGRAM,
                total_followers=data.get("followers_count", 0)
            )
            
            return audience_data
        
        except requests.exceptions.RequestException as e:
            print(f"Instagram API error: {e}")
            return None
        except Exception as e:
            print(f"Error fetching Instagram audience data: {e}")
            return None
    
    def _extract_hashtags(self, caption: str) -> List[str]:
        """
        Extract hashtags from an Instagram caption.
        
        Args:
            caption: Instagram post caption
            
        Returns:
            List of hashtags
        """
        if not caption:
            return []
        
        # Split by spaces and filter for hashtags
        words = caption.split()
        hashtags = [word[1:] for word in words if word.startswith("#")]
        
        return hashtags
    
    def _calculate_engagement_rate(self, engagement: int, impressions: int) -> float:
        """
        Calculate engagement rate for an Instagram post.
        
        Engagement rate = engagement / impressions * 100
        
        Args:
            engagement: Total engagement count
            impressions: Total impression count
            
        Returns:
            Engagement rate as a percentage
        """
        if impressions == 0:
            return 0.0
        
        return engagement / impressions * 100

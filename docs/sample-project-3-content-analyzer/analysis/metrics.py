from typing import List, Dict, Optional, Any
from datetime import datetime
import pandas as pd
import numpy as np

from models import ContentItem, ContentMetrics, Platform


class MetricsAnalyzer:
    """
    Analyzer for content metrics to calculate various performance indicators.
    """
    
    def __init__(self):
        """
        Initialize the metrics analyzer.
        """
        pass
    
    def calculate_average_metrics(self, metrics: List[ContentMetrics]) -> Dict[str, float]:
        """
        Calculate average metrics across all content items.
        
        Args:
            metrics: List of ContentMetrics objects
            
        Returns:
            Dictionary of average metrics
        """
        if not metrics:
            return {}
        
        # Extract metrics into lists
        views = [m.views for m in metrics if m.views is not None]
        likes = [m.likes for m in metrics if m.likes is not None]
        comments = [m.comments for m in metrics if m.comments is not None]
        shares = [m.shares for m in metrics if m.shares is not None]
        saves = [m.saves for m in metrics if m.saves is not None]
        engagement_rates = [m.engagement_rate for m in metrics if m.engagement_rate is not None]
        
        # Calculate averages
        avg_metrics = {}
        
        if views:
            avg_metrics["avg_views"] = sum(views) / len(views)
        
        if likes:
            avg_metrics["avg_likes"] = sum(likes) / len(likes)
        
        if comments:
            avg_metrics["avg_comments"] = sum(comments) / len(comments)
        
        if shares:
            avg_metrics["avg_shares"] = sum(shares) / len(shares)
        
        if saves:
            avg_metrics["avg_saves"] = sum(saves) / len(saves)
        
        if engagement_rates:
            avg_metrics["avg_engagement_rate"] = sum(engagement_rates) / len(engagement_rates)
        
        return avg_metrics
    
    def calculate_platform_metrics(self, metrics: List[ContentMetrics]) -> Dict[Platform, Dict[str, float]]:
        """
        Calculate average metrics grouped by platform.
        
        Args:
            metrics: List of ContentMetrics objects
            
        Returns:
            Dictionary mapping platforms to their average metrics
        """
        if not metrics:
            return {}
        
        # Group metrics by platform
        platform_metrics = {}
        
        for platform in Platform:
            platform_metrics[platform] = [m for m in metrics if m.platform == platform]
        
        # Calculate average metrics for each platform
        result = {}
        
        for platform, platform_metrics_list in platform_metrics.items():
            if platform_metrics_list:
                result[platform] = self.calculate_average_metrics(platform_metrics_list)
        
        return result
    
    def identify_top_performing_content(self, content_items: List[ContentItem], 
                                       metrics: Dict[str, ContentMetrics], 
                                       metric_name: str = "engagement_rate",
                                       limit: int = 5) -> List[str]:
        """
        Identify top performing content based on a specific metric.
        
        Args:
            content_items: List of ContentItem objects
            metrics: Dictionary mapping content IDs to ContentMetrics objects
            metric_name: Name of the metric to use for ranking
            limit: Maximum number of top content items to return
            
        Returns:
            List of content IDs for top performing content
        """
        if not content_items or not metrics:
            return []
        
        # Create a list of (content_id, metric_value) tuples
        content_metrics = []
        
        for item in content_items:
            if item.id in metrics:
                metric_value = getattr(metrics[item.id], metric_name, 0)
                if metric_value is not None:
                    content_metrics.append((item.id, metric_value))
        
        # Sort by metric value in descending order
        content_metrics.sort(key=lambda x: x[1], reverse=True)
        
        # Return top content IDs
        return [content_id for content_id, _ in content_metrics[:limit]]
    
    def calculate_growth_rate(self, current_metrics: Dict[str, float], 
                             previous_metrics: Dict[str, float]) -> Dict[str, float]:
        """
        Calculate growth rate between current and previous metrics.
        
        Args:
            current_metrics: Dictionary of current metrics
            previous_metrics: Dictionary of previous metrics
            
        Returns:
            Dictionary of growth rates as percentages
        """
        if not current_metrics or not previous_metrics:
            return {}
        
        growth_rates = {}
        
        for key in current_metrics:
            if key in previous_metrics and previous_metrics[key] > 0:
                growth_rates[f"{key}_growth"] = ((current_metrics[key] - previous_metrics[key]) / 
                                               previous_metrics[key] * 100)
        
        return growth_rates
    
    def calculate_engagement_distribution(self, metrics: List[ContentMetrics]) -> Dict[str, float]:
        """
        Calculate the distribution of engagement types (likes, comments, shares).
        
        Args:
            metrics: List of ContentMetrics objects
            
        Returns:
            Dictionary with the percentage distribution of engagement types
        """
        if not metrics:
            return {}
        
        # Sum up all engagement metrics
        total_likes = sum(m.likes or 0 for m in metrics)
        total_comments = sum(m.comments or 0 for m in metrics)
        total_shares = sum(m.shares or 0 for m in metrics)
        
        total_engagement = total_likes + total_comments + total_shares
        
        if total_engagement == 0:
            return {
                "likes_percentage": 0,
                "comments_percentage": 0,
                "shares_percentage": 0
            }
        
        return {
            "likes_percentage": (total_likes / total_engagement) * 100,
            "comments_percentage": (total_comments / total_engagement) * 100,
            "shares_percentage": (total_shares / total_engagement) * 100
        }
    
    def calculate_posting_frequency(self, content_items: List[ContentItem]) -> Dict[str, Any]:
        """
        Calculate posting frequency statistics.
        
        Args:
            content_items: List of ContentItem objects
            
        Returns:
            Dictionary with posting frequency statistics
        """
        if not content_items or len(content_items) < 2:
            return {
                "avg_posts_per_week": 0,
                "avg_posts_per_month": 0,
                "most_active_day": None
            }
        
        # Convert published_at strings to datetime objects
        dates = []
        for item in content_items:
            try:
                date = datetime.fromisoformat(item.published_at.replace("Z", "+00:00"))
                dates.append(date)
            except (ValueError, AttributeError):
                continue
        
        if not dates or len(dates) < 2:
            return {
                "avg_posts_per_week": 0,
                "avg_posts_per_month": 0,
                "most_active_day": None
            }
        
        # Sort dates
        dates.sort()
        
        # Calculate date range in days
        date_range_days = (dates[-1] - dates[0]).days
        
        if date_range_days == 0:
            return {
                "avg_posts_per_week": len(dates) * 7,
                "avg_posts_per_month": len(dates) * 30,
                "most_active_day": dates[0].strftime("%A")
            }
        
        # Calculate average posts per week and month
        avg_posts_per_day = len(dates) / date_range_days
        avg_posts_per_week = avg_posts_per_day * 7
        avg_posts_per_month = avg_posts_per_day * 30
        
        # Find most active day of the week
        day_counts = {}
        for date in dates:
            day_name = date.strftime("%A")
            day_counts[day_name] = day_counts.get(day_name, 0) + 1
        
        most_active_day = max(day_counts.items(), key=lambda x: x[1])[0]
        
        return {
            "avg_posts_per_week": avg_posts_per_week,
            "avg_posts_per_month": avg_posts_per_month,
            "most_active_day": most_active_day
        }
    
    def calculate_best_posting_times(self, content_items: List[ContentItem], 
                                    metrics: Dict[str, ContentMetrics],
                                    metric_name: str = "engagement_rate") -> Dict[str, Any]:
        """
        Calculate the best times to post based on engagement metrics.
        
        Args:
            content_items: List of ContentItem objects
            metrics: Dictionary mapping content IDs to ContentMetrics objects
            metric_name: Name of the metric to use for analysis
            
        Returns:
            Dictionary with best posting times
        """
        if not content_items or not metrics:
            return {
                "best_day": None,
                "best_hour": None
            }
        
        # Create a list of (hour, day_of_week, metric_value) tuples
        time_metrics = []
        
        for item in content_items:
            if item.id in metrics:
                try:
                    date = datetime.fromisoformat(item.published_at.replace("Z", "+00:00"))
                    hour = date.hour
                    day_of_week = date.strftime("%A")
                    metric_value = getattr(metrics[item.id], metric_name, 0)
                    
                    if metric_value is not None:
                        time_metrics.append((hour, day_of_week, metric_value))
                except (ValueError, AttributeError):
                    continue
        
        if not time_metrics:
            return {
                "best_day": None,
                "best_hour": None
            }
        
        # Group by day of week
        day_metrics = {}
        for hour, day, value in time_metrics:
            if day not in day_metrics:
                day_metrics[day] = []
            day_metrics[day].append(value)
        
        # Calculate average metric value for each day
        day_averages = {}
        for day, values in day_metrics.items():
            day_averages[day] = sum(values) / len(values)
        
        # Find best day
        best_day = max(day_averages.items(), key=lambda x: x[1])[0]
        
        # Group by hour
        hour_metrics = {}
        for hour, day, value in time_metrics:
            if hour not in hour_metrics:
                hour_metrics[hour] = []
            hour_metrics[hour].append(value)
        
        # Calculate average metric value for each hour
        hour_averages = {}
        for hour, values in hour_metrics.items():
            hour_averages[hour] = sum(values) / len(values)
        
        # Find best hour
        best_hour = max(hour_averages.items(), key=lambda x: x[1])[0]
        
        return {
            "best_day": best_day,
            "best_hour": best_hour
        }

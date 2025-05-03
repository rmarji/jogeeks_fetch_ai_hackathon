from typing import List, Dict, Optional, Any, Tuple
from datetime import datetime

from models import (
    ContentItem, 
    ContentMetrics, 
    Platform, 
    ContentType, 
    PerformanceInsight
)


class InsightGenerator:
    """
    Generator for insights based on content performance analysis.
    """
    
    def __init__(self):
        """
        Initialize the insight generator.
        """
        pass
    
    def generate_content_type_insights(self, content_type_performance: Dict[ContentType, float]) -> List[PerformanceInsight]:
        """
        Generate insights based on content type performance.
        
        Args:
            content_type_performance: Dictionary mapping content types to average engagement rates
            
        Returns:
            List of PerformanceInsight objects
        """
        if not content_type_performance:
            return []
        
        insights = []
        
        # Find best performing content type
        best_type = max(content_type_performance.items(), key=lambda x: x[1])
        
        insights.append(PerformanceInsight.create(
            insight_type="content_type",
            description=f"{best_type[0].value.capitalize()} content performs best with an average engagement rate of {best_type[1]:.2f}%.",
            confidence=0.8,
            supporting_data={"content_type_performance": {k.value: v for k, v in content_type_performance.items()}}
        ))
        
        # Compare content types
        if len(content_type_performance) > 1:
            sorted_types = sorted(content_type_performance.items(), key=lambda x: x[1], reverse=True)
            
            comparison = f"Content type performance ranking: "
            comparison += ", ".join([f"{t[0].value.capitalize()} ({t[1]:.2f}%)" for t in sorted_types])
            
            insights.append(PerformanceInsight.create(
                insight_type="content_type_comparison",
                description=comparison,
                confidence=0.7,
                supporting_data={"content_type_performance": {k.value: v for k, v in content_type_performance.items()}}
            ))
        
        return insights
    
    def generate_platform_insights(self, platform_performance: Dict[Platform, float]) -> List[PerformanceInsight]:
        """
        Generate insights based on platform performance.
        
        Args:
            platform_performance: Dictionary mapping platforms to average engagement rates
            
        Returns:
            List of PerformanceInsight objects
        """
        if not platform_performance:
            return []
        
        insights = []
        
        # Find best performing platform
        best_platform = max(platform_performance.items(), key=lambda x: x[1])
        
        insights.append(PerformanceInsight.create(
            insight_type="platform",
            description=f"{best_platform[0].value.capitalize()} performs best with an average engagement rate of {best_platform[1]:.2f}%.",
            confidence=0.8,
            supporting_data={"platform_performance": {k.value: v for k, v in platform_performance.items()}}
        ))
        
        # Compare platforms
        if len(platform_performance) > 1:
            sorted_platforms = sorted(platform_performance.items(), key=lambda x: x[1], reverse=True)
            
            comparison = f"Platform performance ranking: "
            comparison += ", ".join([f"{p[0].value.capitalize()} ({p[1]:.2f}%)" for p in sorted_platforms])
            
            insights.append(PerformanceInsight.create(
                insight_type="platform_comparison",
                description=comparison,
                confidence=0.7,
                supporting_data={"platform_performance": {k.value: v for k, v in platform_performance.items()}}
            ))
        
        return insights
    
    def generate_topic_insights(self, popular_topics: List[Tuple[str, float]]) -> List[PerformanceInsight]:
        """
        Generate insights based on popular topics.
        
        Args:
            popular_topics: List of (topic, average_engagement_rate) tuples
            
        Returns:
            List of PerformanceInsight objects
        """
        if not popular_topics:
            return []
        
        insights = []
        
        # Generate insight for top topic
        top_topic = popular_topics[0]
        
        insights.append(PerformanceInsight.create(
            insight_type="topic",
            description=f"Content about '{top_topic[0]}' performs best with an average engagement rate of {top_topic[1]:.2f}%.",
            confidence=0.7,
            supporting_data={"popular_topics": [(t[0], t[1]) for t in popular_topics]}
        ))
        
        # Generate insight for all top topics
        if len(popular_topics) > 1:
            topics_list = ", ".join([f"'{t[0]}'" for t in popular_topics[:3]])
            
            insights.append(PerformanceInsight.create(
                insight_type="topics",
                description=f"Top performing topics include {topics_list}. Consider creating more content around these topics.",
                confidence=0.6,
                supporting_data={"popular_topics": [(t[0], t[1]) for t in popular_topics]}
            ))
        
        return insights
    
    def generate_hashtag_insights(self, popular_hashtags: List[Tuple[str, float]]) -> List[PerformanceInsight]:
        """
        Generate insights based on popular hashtags.
        
        Args:
            popular_hashtags: List of (hashtag, average_engagement_rate) tuples
            
        Returns:
            List of PerformanceInsight objects
        """
        if not popular_hashtags:
            return []
        
        insights = []
        
        # Generate insight for top hashtag
        top_hashtag = popular_hashtags[0]
        
        insights.append(PerformanceInsight.create(
            insight_type="hashtag",
            description=f"Content with the hashtag '#{top_hashtag[0]}' performs best with an average engagement rate of {top_hashtag[1]:.2f}%.",
            confidence=0.7,
            supporting_data={"popular_hashtags": [(h[0], h[1]) for h in popular_hashtags]}
        ))
        
        # Generate insight for all top hashtags
        if len(popular_hashtags) > 1:
            hashtags_list = ", ".join([f"#{h[0]}" for h in popular_hashtags[:5]])
            
            insights.append(PerformanceInsight.create(
                insight_type="hashtags",
                description=f"Top performing hashtags include {hashtags_list}. Consider using these hashtags in future content.",
                confidence=0.6,
                supporting_data={"popular_hashtags": [(h[0], h[1]) for h in popular_hashtags]}
            ))
        
        return insights
    
    def generate_content_length_insights(self, length_performance: Dict[str, float]) -> List[PerformanceInsight]:
        """
        Generate insights based on content length performance.
        
        Args:
            length_performance: Dictionary mapping length categories to average engagement rates
            
        Returns:
            List of PerformanceInsight objects
        """
        if not length_performance:
            return []
        
        insights = []
        
        # Find best performing length category
        best_length = max(length_performance.items(), key=lambda x: x[1])
        
        length_descriptions = {
            "short": "short (less than 100 characters)",
            "medium": "medium (100-500 characters)",
            "long": "long (more than 500 characters)"
        }
        
        insights.append(PerformanceInsight.create(
            insight_type="content_length",
            description=f"{length_descriptions[best_length[0]].capitalize()} content performs best with an average engagement rate of {best_length[1]:.2f}%.",
            confidence=0.7,
            supporting_data={"length_performance": length_performance}
        ))
        
        # Compare length categories
        if len(length_performance) > 1:
            sorted_lengths = sorted(length_performance.items(), key=lambda x: x[1], reverse=True)
            
            comparison = f"Content length performance ranking: "
            comparison += ", ".join([f"{length_descriptions[l[0]]} ({l[1]:.2f}%)" for l in sorted_lengths])
            
            insights.append(PerformanceInsight.create(
                insight_type="content_length_comparison",
                description=comparison,
                confidence=0.6,
                supporting_data={"length_performance": length_performance}
            ))
        
        return insights
    
    def generate_posting_time_insights(self, best_posting_times: Dict[str, Any]) -> List[PerformanceInsight]:
        """
        Generate insights based on best posting times.
        
        Args:
            best_posting_times: Dictionary with best posting times
            
        Returns:
            List of PerformanceInsight objects
        """
        if not best_posting_times:
            return []
        
        insights = []
        
        best_day = best_posting_times.get("best_day")
        best_hour = best_posting_times.get("best_hour")
        
        if best_day:
            insights.append(PerformanceInsight.create(
                insight_type="posting_day",
                description=f"Content posted on {best_day} tends to perform better than other days.",
                confidence=0.6,
                supporting_data={"best_posting_times": best_posting_times}
            ))
        
        if best_hour is not None:
            # Convert 24-hour format to 12-hour format
            hour_12 = best_hour % 12
            if hour_12 == 0:
                hour_12 = 12
            
            am_pm = "AM" if best_hour < 12 else "PM"
            
            insights.append(PerformanceInsight.create(
                insight_type="posting_time",
                description=f"Content posted around {hour_12} {am_pm} tends to perform better than other times.",
                confidence=0.6,
                supporting_data={"best_posting_times": best_posting_times}
            ))
        
        if best_day and best_hour is not None:
            # Convert 24-hour format to 12-hour format
            hour_12 = best_hour % 12
            if hour_12 == 0:
                hour_12 = 12
            
            am_pm = "AM" if best_hour < 12 else "PM"
            
            insights.append(PerformanceInsight.create(
                insight_type="optimal_posting_schedule",
                description=f"For optimal engagement, consider posting on {best_day} around {hour_12} {am_pm}.",
                confidence=0.7,
                supporting_data={"best_posting_times": best_posting_times}
            ))
        
        return insights
    
    def generate_seasonal_insights(self, seasonal_performance: Dict[str, float]) -> List[PerformanceInsight]:
        """
        Generate insights based on seasonal performance.
        
        Args:
            seasonal_performance: Dictionary mapping months to average engagement rates
            
        Returns:
            List of PerformanceInsight objects
        """
        if not seasonal_performance:
            return []
        
        insights = []
        
        # Find best performing month
        best_month = max(seasonal_performance.items(), key=lambda x: x[1])
        
        insights.append(PerformanceInsight.create(
            insight_type="seasonal",
            description=f"Content posted in {best_month[0]} performs best with an average engagement rate of {best_month[1]:.2f}%.",
            confidence=0.6,
            supporting_data={"seasonal_performance": seasonal_performance}
        ))
        
        # Group months into seasons
        winter = ["December", "January", "February"]
        spring = ["March", "April", "May"]
        summer = ["June", "July", "August"]
        fall = ["September", "October", "November"]
        
        seasons = {
            "Winter": [seasonal_performance.get(month, 0) for month in winter if month in seasonal_performance],
            "Spring": [seasonal_performance.get(month, 0) for month in spring if month in seasonal_performance],
            "Summer": [seasonal_performance.get(month, 0) for month in summer if month in seasonal_performance],
            "Fall": [seasonal_performance.get(month, 0) for month in fall if month in seasonal_performance]
        }
        
        # Calculate average engagement rate for each season
        season_performance = {}
        
        for season, rates in seasons.items():
            if rates:
                season_performance[season] = sum(rates) / len(rates)
        
        if season_performance:
            # Find best performing season
            best_season = max(season_performance.items(), key=lambda x: x[1])
            
            insights.append(PerformanceInsight.create(
                insight_type="seasonal_trend",
                description=f"{best_season[0]} months tend to have higher engagement rates (avg: {best_season[1]:.2f}%).",
                confidence=0.5,
                supporting_data={"season_performance": season_performance}
            ))
        
        return insights
    
    def generate_growth_insights(self, growth_rates: Dict[str, float]) -> List[PerformanceInsight]:
        """
        Generate insights based on growth rates.
        
        Args:
            growth_rates: Dictionary of growth rates as percentages
            
        Returns:
            List of PerformanceInsight objects
        """
        if not growth_rates:
            return []
        
        insights = []
        
        # Generate insights for each growth metric
        for metric, rate in growth_rates.items():
            if "views" in metric:
                metric_name = "Views"
            elif "likes" in metric:
                metric_name = "Likes"
            elif "comments" in metric:
                metric_name = "Comments"
            elif "engagement" in metric:
                metric_name = "Engagement rate"
            else:
                metric_name = metric.replace("_growth", "").capitalize()
            
            if rate > 0:
                insights.append(PerformanceInsight.create(
                    insight_type="growth",
                    description=f"{metric_name} increased by {rate:.2f}% compared to the previous period.",
                    confidence=0.7,
                    supporting_data={"growth_rates": growth_rates}
                ))
            elif rate < 0:
                insights.append(PerformanceInsight.create(
                    insight_type="decline",
                    description=f"{metric_name} decreased by {abs(rate):.2f}% compared to the previous period.",
                    confidence=0.7,
                    supporting_data={"growth_rates": growth_rates}
                ))
        
        # Generate overall growth insight
        avg_growth = sum(growth_rates.values()) / len(growth_rates)
        
        if avg_growth > 5:
            insights.append(PerformanceInsight.create(
                insight_type="overall_growth",
                description=f"Overall performance is improving with an average growth of {avg_growth:.2f}% across all metrics.",
                confidence=0.6,
                supporting_data={"growth_rates": growth_rates, "avg_growth": avg_growth}
            ))
        elif avg_growth < -5:
            insights.append(PerformanceInsight.create(
                insight_type="overall_decline",
                description=f"Overall performance is declining with an average decrease of {abs(avg_growth):.2f}% across all metrics.",
                confidence=0.6,
                supporting_data={"growth_rates": growth_rates, "avg_growth": avg_growth}
            ))
        
        return insights
    
    def generate_recommendations(self, insights: List[PerformanceInsight]) -> List[str]:
        """
        Generate recommendations based on insights.
        
        Args:
            insights: List of PerformanceInsight objects
            
        Returns:
            List of recommendation strings
        """
        if not insights:
            return []
        
        recommendations = []
        
        # Process insights by type
        content_type_insights = [i for i in insights if i.insight_type == "content_type"]
        platform_insights = [i for i in insights if i.insight_type == "platform"]
        topic_insights = [i for i in insights if i.insight_type == "topic" or i.insight_type == "topics"]
        hashtag_insights = [i for i in insights if i.insight_type == "hashtag" or i.insight_type == "hashtags"]
        length_insights = [i for i in insights if i.insight_type == "content_length"]
        time_insights = [i for i in insights if i.insight_type == "optimal_posting_schedule"]
        growth_insights = [i for i in insights if i.insight_type == "growth" or i.insight_type == "decline"]
        
        # Generate recommendations based on content type insights
        if content_type_insights:
            insight = content_type_insights[0]
            supporting_data = insight.supporting_data or {}
            content_type_performance = supporting_data.get("content_type_performance", {})
            
            if content_type_performance:
                best_type = max(content_type_performance.items(), key=lambda x: x[1])[0]
                recommendations.append(f"Create more {best_type} content to maximize engagement.")
        
        # Generate recommendations based on platform insights
        if platform_insights:
            insight = platform_insights[0]
            supporting_data = insight.supporting_data or {}
            platform_performance = supporting_data.get("platform_performance", {})
            
            if platform_performance:
                best_platform = max(platform_performance.items(), key=lambda x: x[1])[0]
                recommendations.append(f"Focus more on {best_platform.capitalize()} where your content performs best.")
        
        # Generate recommendations based on topic insights
        if topic_insights:
            for insight in topic_insights:
                if insight.insight_type == "topics":
                    supporting_data = insight.supporting_data or {}
                    popular_topics = supporting_data.get("popular_topics", [])
                    
                    if popular_topics:
                        topics = [t[0] for t in popular_topics[:3]]
                        topics_str = ", ".join([f"'{t}'" for t in topics])
                        recommendations.append(f"Create more content around popular topics: {topics_str}.")
                    
                    break
        
        # Generate recommendations based on hashtag insights
        if hashtag_insights:
            for insight in hashtag_insights:
                if insight.insight_type == "hashtags":
                    supporting_data = insight.supporting_data or {}
                    popular_hashtags = supporting_data.get("popular_hashtags", [])
                    
                    if popular_hashtags:
                        hashtags = [h[0] for h in popular_hashtags[:5]]
                        hashtags_str = ", ".join([f"#{h}" for h in hashtags])
                        recommendations.append(f"Use these high-performing hashtags in your content: {hashtags_str}.")
                    
                    break
        
        # Generate recommendations based on content length insights
        if length_insights:
            insight = length_insights[0]
            supporting_data = insight.supporting_data or {}
            length_performance = supporting_data.get("length_performance", {})
            
            if length_performance:
                best_length = max(length_performance.items(), key=lambda x: x[1])[0]
                
                if best_length == "short":
                    recommendations.append("Keep your content descriptions concise (under 100 characters) for better engagement.")
                elif best_length == "medium":
                    recommendations.append("Aim for medium-length descriptions (100-500 characters) for optimal engagement.")
                elif best_length == "long":
                    recommendations.append("Detailed descriptions (over 500 characters) perform well with your audience.")
        
        # Generate recommendations based on posting time insights
        if time_insights:
            insight = time_insights[0]
            recommendations.append(insight.description)
        
        # Generate recommendations based on growth insights
        if growth_insights:
            declining_metrics = []
            
            for insight in growth_insights:
                if insight.insight_type == "decline":
                    description = insight.description.lower()
                    
                    if "views" in description:
                        declining_metrics.append("views")
                    elif "likes" in description:
                        declining_metrics.append("likes")
                    elif "comments" in description:
                        declining_metrics.append("comments")
                    elif "engagement" in description:
                        declining_metrics.append("engagement")
            
            if declining_metrics:
                metrics_str = ", ".join(declining_metrics)
                recommendations.append(f"Focus on improving {metrics_str} which have been declining recently.")
        
        # Add general recommendations if we don't have many specific ones
        if len(recommendations) < 3:
            recommendations.append("Experiment with different content formats to identify what resonates best with your audience.")
            recommendations.append("Engage with your audience by responding to comments to boost overall engagement.")
            recommendations.append("Analyze your competitors' top-performing content for inspiration.")
        
        return recommendations

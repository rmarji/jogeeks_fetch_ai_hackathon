from typing import List, Dict, Optional, Any, Tuple
from collections import Counter
import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import pandas as pd
import numpy as np

from models import ContentItem, ContentMetrics, Platform, ContentType


class PatternAnalyzer:
    """
    Analyzer for identifying patterns in content performance.
    """
    
    def __init__(self):
        """
        Initialize the pattern analyzer.
        """
        # Download NLTK resources if needed
        try:
            nltk.data.find('tokenizers/punkt')
            nltk.data.find('corpora/stopwords')
        except LookupError:
            nltk.download('punkt')
            nltk.download('stopwords')
        
        self.stop_words = set(stopwords.words('english'))
    
    def identify_content_type_performance(self, content_items: List[ContentItem], 
                                         metrics: Dict[str, ContentMetrics]) -> Dict[ContentType, float]:
        """
        Identify which content types perform best.
        
        Args:
            content_items: List of ContentItem objects
            metrics: Dictionary mapping content IDs to ContentMetrics objects
            
        Returns:
            Dictionary mapping content types to average engagement rates
        """
        if not content_items or not metrics:
            return {}
        
        # Group content by type
        content_by_type = {}
        
        for item in content_items:
            if item.content_type not in content_by_type:
                content_by_type[item.content_type] = []
            
            if item.id in metrics:
                content_by_type[item.content_type].append(metrics[item.id])
        
        # Calculate average engagement rate for each content type
        result = {}
        
        for content_type, content_metrics in content_by_type.items():
            if content_metrics:
                engagement_rates = [m.engagement_rate for m in content_metrics if m.engagement_rate is not None]
                if engagement_rates:
                    result[content_type] = sum(engagement_rates) / len(engagement_rates)
        
        return result
    
    def identify_platform_performance(self, content_items: List[ContentItem], 
                                     metrics: Dict[str, ContentMetrics]) -> Dict[Platform, float]:
        """
        Identify which platforms perform best.
        
        Args:
            content_items: List of ContentItem objects
            metrics: Dictionary mapping content IDs to ContentMetrics objects
            
        Returns:
            Dictionary mapping platforms to average engagement rates
        """
        if not content_items or not metrics:
            return {}
        
        # Group content by platform
        content_by_platform = {}
        
        for item in content_items:
            if item.platform not in content_by_platform:
                content_by_platform[item.platform] = []
            
            if item.id in metrics:
                content_by_platform[item.platform].append(metrics[item.id])
        
        # Calculate average engagement rate for each platform
        result = {}
        
        for platform, platform_metrics in content_by_platform.items():
            if platform_metrics:
                engagement_rates = [m.engagement_rate for m in platform_metrics if m.engagement_rate is not None]
                if engagement_rates:
                    result[platform] = sum(engagement_rates) / len(engagement_rates)
        
        return result
    
    def identify_popular_topics(self, content_items: List[ContentItem], 
                               metrics: Dict[str, ContentMetrics],
                               top_n: int = 5) -> List[Tuple[str, float]]:
        """
        Identify popular topics based on content titles and descriptions.
        
        Args:
            content_items: List of ContentItem objects
            metrics: Dictionary mapping content IDs to ContentMetrics objects
            top_n: Number of top topics to return
            
        Returns:
            List of (topic, average_engagement_rate) tuples
        """
        if not content_items or not metrics:
            return []
        
        # Extract keywords from titles and descriptions
        keywords = []
        
        for item in content_items:
            # Extract keywords from title
            if item.title:
                title_keywords = self._extract_keywords(item.title)
                keywords.extend([(kw, item.id) for kw in title_keywords])
            
            # Extract keywords from description
            if item.description:
                desc_keywords = self._extract_keywords(item.description)
                keywords.extend([(kw, item.id) for kw in desc_keywords])
        
        if not keywords:
            return []
        
        # Group by keyword
        keyword_content_ids = {}
        
        for keyword, content_id in keywords:
            if keyword not in keyword_content_ids:
                keyword_content_ids[keyword] = set()
            
            keyword_content_ids[keyword].add(content_id)
        
        # Calculate average engagement rate for each keyword
        keyword_metrics = []
        
        for keyword, content_ids in keyword_content_ids.items():
            # Only consider keywords that appear in multiple content items
            if len(content_ids) < 2:
                continue
            
            # Calculate average engagement rate
            engagement_rates = []
            
            for content_id in content_ids:
                if content_id in metrics and metrics[content_id].engagement_rate is not None:
                    engagement_rates.append(metrics[content_id].engagement_rate)
            
            if engagement_rates:
                avg_engagement_rate = sum(engagement_rates) / len(engagement_rates)
                keyword_metrics.append((keyword, avg_engagement_rate))
        
        # Sort by engagement rate in descending order
        keyword_metrics.sort(key=lambda x: x[1], reverse=True)
        
        # Return top N keywords
        return keyword_metrics[:top_n]
    
    def identify_popular_hashtags(self, content_items: List[ContentItem], 
                                 metrics: Dict[str, ContentMetrics],
                                 top_n: int = 5) -> List[Tuple[str, float]]:
        """
        Identify popular hashtags based on content tags.
        
        Args:
            content_items: List of ContentItem objects
            metrics: Dictionary mapping content IDs to ContentMetrics objects
            top_n: Number of top hashtags to return
            
        Returns:
            List of (hashtag, average_engagement_rate) tuples
        """
        if not content_items or not metrics:
            return []
        
        # Extract hashtags from content tags
        hashtags = []
        
        for item in content_items:
            if item.tags:
                hashtags.extend([(tag, item.id) for tag in item.tags])
        
        if not hashtags:
            return []
        
        # Group by hashtag
        hashtag_content_ids = {}
        
        for hashtag, content_id in hashtags:
            if hashtag not in hashtag_content_ids:
                hashtag_content_ids[hashtag] = set()
            
            hashtag_content_ids[hashtag].add(content_id)
        
        # Calculate average engagement rate for each hashtag
        hashtag_metrics = []
        
        for hashtag, content_ids in hashtag_content_ids.items():
            # Only consider hashtags that appear in multiple content items
            if len(content_ids) < 2:
                continue
            
            # Calculate average engagement rate
            engagement_rates = []
            
            for content_id in content_ids:
                if content_id in metrics and metrics[content_id].engagement_rate is not None:
                    engagement_rates.append(metrics[content_id].engagement_rate)
            
            if engagement_rates:
                avg_engagement_rate = sum(engagement_rates) / len(engagement_rates)
                hashtag_metrics.append((hashtag, avg_engagement_rate))
        
        # Sort by engagement rate in descending order
        hashtag_metrics.sort(key=lambda x: x[1], reverse=True)
        
        # Return top N hashtags
        return hashtag_metrics[:top_n]
    
    def identify_content_length_performance(self, content_items: List[ContentItem], 
                                          metrics: Dict[str, ContentMetrics]) -> Dict[str, float]:
        """
        Identify how content length affects performance.
        
        Args:
            content_items: List of ContentItem objects
            metrics: Dictionary mapping content IDs to ContentMetrics objects
            
        Returns:
            Dictionary mapping length categories to average engagement rates
        """
        if not content_items or not metrics:
            return {}
        
        # Categorize content by description length
        short_content = []
        medium_content = []
        long_content = []
        
        for item in content_items:
            if item.id not in metrics:
                continue
            
            if not item.description:
                continue
            
            length = len(item.description)
            
            if length < 100:
                short_content.append(metrics[item.id])
            elif length < 500:
                medium_content.append(metrics[item.id])
            else:
                long_content.append(metrics[item.id])
        
        # Calculate average engagement rate for each length category
        result = {}
        
        if short_content:
            engagement_rates = [m.engagement_rate for m in short_content if m.engagement_rate is not None]
            if engagement_rates:
                result["short"] = sum(engagement_rates) / len(engagement_rates)
        
        if medium_content:
            engagement_rates = [m.engagement_rate for m in medium_content if m.engagement_rate is not None]
            if engagement_rates:
                result["medium"] = sum(engagement_rates) / len(engagement_rates)
        
        if long_content:
            engagement_rates = [m.engagement_rate for m in long_content if m.engagement_rate is not None]
            if engagement_rates:
                result["long"] = sum(engagement_rates) / len(engagement_rates)
        
        return result
    
    def identify_seasonal_patterns(self, content_items: List[ContentItem], 
                                  metrics: Dict[str, ContentMetrics]) -> Dict[str, float]:
        """
        Identify seasonal patterns in content performance.
        
        Args:
            content_items: List of ContentItem objects
            metrics: Dictionary mapping content IDs to ContentMetrics objects
            
        Returns:
            Dictionary mapping months to average engagement rates
        """
        if not content_items or not metrics:
            return {}
        
        # Group content by month
        content_by_month = {}
        
        for item in content_items:
            if item.id not in metrics:
                continue
            
            try:
                date = datetime.fromisoformat(item.published_at.replace("Z", "+00:00"))
                month = date.strftime("%B")  # Month name
                
                if month not in content_by_month:
                    content_by_month[month] = []
                
                content_by_month[month].append(metrics[item.id])
            except (ValueError, AttributeError):
                continue
        
        # Calculate average engagement rate for each month
        result = {}
        
        for month, month_metrics in content_by_month.items():
            if month_metrics:
                engagement_rates = [m.engagement_rate for m in month_metrics if m.engagement_rate is not None]
                if engagement_rates:
                    result[month] = sum(engagement_rates) / len(engagement_rates)
        
        return result
    
    def _extract_keywords(self, text: str) -> List[str]:
        """
        Extract keywords from text.
        
        Args:
            text: Text to extract keywords from
            
        Returns:
            List of keywords
        """
        # Tokenize text
        tokens = word_tokenize(text.lower())
        
        # Remove stop words and non-alphabetic tokens
        keywords = [word for word in tokens if word.isalpha() and word not in self.stop_words and len(word) > 3]
        
        return keywords

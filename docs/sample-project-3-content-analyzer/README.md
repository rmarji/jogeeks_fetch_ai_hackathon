# Content Performance Analyzer

A powerful agent that analyzes content performance across multiple social media platforms, identifies patterns, and generates actionable insights for content creators.

## Overview

This project demonstrates the capabilities of the Agentverse platform by implementing a practical tool for the Creator Economy. The Content Performance Analyzer helps content creators understand how their content is performing across different platforms, identify what works best, and get actionable recommendations to improve their content strategy.

### Key Features

- **Multi-Platform Analysis**: Analyze content performance across YouTube, Instagram, TikTok, and more
- **Performance Metrics**: Track views, likes, comments, shares, and engagement rates
- **Pattern Recognition**: Identify which content types, topics, and hashtags perform best
- **Actionable Insights**: Get data-driven insights about your content performance
- **Customizable Reports**: Generate daily, weekly, or monthly performance reports
- **Optimization Recommendations**: Receive specific recommendations to improve your content strategy

## System Architecture

The system consists of a single agent with multiple components:

1. **Platform Connectors**: Connect to social media APIs to fetch content and metrics
2. **Analysis Modules**: Analyze performance data to identify patterns and trends
3. **Insight Generator**: Generate actionable insights based on the analysis
4. **Report Generator**: Create comprehensive performance reports

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- API keys for the social media platforms you want to analyze

### Setup

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd sample-project-3-content-analyzer
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file from the template:
   ```bash
   cp .env.template .env
   ```

5. Edit the `.env` file to add your API keys and customize settings:
   ```
   # API Keys for social media platforms
   YOUTUBE_API_KEY=your_youtube_api_key_here
   YOUTUBE_CHANNEL_ID=your_youtube_channel_id_here
   
   INSTAGRAM_ACCESS_TOKEN=your_instagram_access_token_here
   INSTAGRAM_USER_ID=your_instagram_user_id_here
   
   TIKTOK_ACCESS_TOKEN=your_tiktok_access_token_here
   TIKTOK_OPEN_ID=your_tiktok_open_id_here
   
   # Analysis settings
   DEFAULT_PLATFORMS=YOUTUBE,INSTAGRAM,TIKTOK
   DEFAULT_TIME_FRAME=WEEK
   DEFAULT_REPORT_SCHEDULE=WEEKLY
   ```

## Usage

### Running the Content Analyzer Agent

To start the Content Analyzer Agent:

```bash
python content_analyzer.py
```

The agent will start and begin monitoring your content performance according to the settings in your `.env` file.

### Using the Client

A sample client is provided to demonstrate how to interact with the Content Analyzer Agent:

```bash
python client.py
```

Before running the client, make sure to set the `CONTENT_ANALYZER_ADDRESS` environment variable to the address of your running Content Analyzer Agent. You can find this address in the agent's startup logs.

### API Endpoints

The Content Analyzer Agent provides the following API endpoints:

#### Fetch Content

Request content items from specified platforms:

```python
await ctx.send(CONTENT_ANALYZER_ADDRESS, FetchContentRequest(
    platforms=[Platform.YOUTUBE, Platform.INSTAGRAM],
    start_date="2023-01-01T00:00:00",
    end_date="2023-01-31T23:59:59",
    limit=10
))
```

#### Fetch Metrics

Request metrics for specific content items:

```python
await ctx.send(CONTENT_ANALYZER_ADDRESS, FetchMetricsRequest(
    content_ids=["video123", "post456"]
))
```

#### Generate Report

Request a performance report for a specific time frame:

```python
await ctx.send(CONTENT_ANALYZER_ADDRESS, GenerateReportRequest(
    time_frame=TimeFrame.WEEK,
    platforms=[Platform.YOUTUBE, Platform.INSTAGRAM, Platform.TIKTOK],
    include_recommendations=True
))
```

#### Get Insights

Request insights about your content performance:

```python
await ctx.send(CONTENT_ANALYZER_ADDRESS, GetInsightsRequest(
    limit=5
))
```

## How It Works

### Data Collection

The Content Analyzer Agent connects to social media APIs to fetch:

1. **Content Items**: Videos, posts, reels, etc.
2. **Performance Metrics**: Views, likes, comments, shares, etc.
3. **Audience Data**: Follower counts, demographics, etc.

### Analysis

The agent analyzes the collected data to identify:

1. **Top Performing Content**: Which content items perform best
2. **Content Type Performance**: Which types of content (video, image, etc.) perform best
3. **Platform Performance**: Which platforms provide the best engagement
4. **Topic Analysis**: Which topics resonate most with your audience
5. **Hashtag Analysis**: Which hashtags drive the most engagement
6. **Posting Patterns**: Best times and days to post
7. **Seasonal Trends**: How performance varies over time

### Insights and Recommendations

Based on the analysis, the agent generates:

1. **Performance Insights**: Data-driven observations about your content performance
2. **Actionable Recommendations**: Specific suggestions to improve your content strategy
3. **Performance Reports**: Comprehensive reports summarizing your content performance

## Project Structure

```
sample-project-3-content-analyzer/
├── README.md                       # Project documentation
├── .env.template                   # Template for environment variables
├── requirements.txt                # Project dependencies
├── content_analyzer.py             # Main agent implementation
├── client.py                       # Sample client for interacting with the agent
├── models.py                       # Data models for the agent
├── platform_connectors/            # Connectors for social media platforms
│   ├── __init__.py
│   ├── youtube.py                  # YouTube API connector
│   ├── instagram.py                # Instagram API connector
│   └── tiktok.py                   # TikTok API connector
└── analysis/                       # Analysis modules
    ├── __init__.py
    ├── metrics.py                  # Metrics analysis
    ├── patterns.py                 # Pattern recognition
    └── insights.py                 # Insight generation
```

## Extension Ideas

Here are some ways to extend this project:

1. **Additional Platforms**: Add support for Twitter, Facebook, LinkedIn, etc.
2. **Advanced Analytics**: Implement more sophisticated analysis techniques like sentiment analysis
3. **Competitive Analysis**: Compare your content performance against competitors
4. **Content Calendar**: Generate an optimal content calendar based on performance data
5. **Automated Posting**: Schedule and post content at optimal times
6. **Web Dashboard**: Create a web interface to visualize performance data
7. **Email Reports**: Send performance reports via email
8. **Content Suggestions**: Generate content ideas based on performance data
9. **A/B Testing**: Implement A/B testing for content optimization
10. **AI-Powered Insights**: Use machine learning to generate more advanced insights

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [Fetch.ai](https://fetch.ai/) for the uAgents framework
- [YouTube API](https://developers.google.com/youtube/v3) for YouTube data
- [Instagram Graph API](https://developers.facebook.com/docs/instagram-api/) for Instagram data
- [TikTok for Developers](https://developers.tiktok.com/) for TikTok data

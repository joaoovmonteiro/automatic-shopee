import logging
from datetime import datetime, timedelta, date
from app import db
from models import Analytics, Post, Product
from sqlalchemy import func
import json

logger = logging.getLogger(__name__)

class AnalyticsService:
    """Service for handling analytics operations"""
    
    def __init__(self):
        pass
    
    def update_daily_analytics(self, target_date=None):
        """Update analytics data for a specific date"""
        try:
            if target_date is None:
                target_date = datetime.now().date()
            
            platforms = ['instagram', 'facebook', 'twitter']
            
            for platform in platforms:
                # Get posts for the date and platform
                posts = Post.query.filter(
                    func.date(Post.created_at) == target_date,
                    Post.platform == platform,
                    Post.status == 'posted'
                ).all()
                
                # Calculate metrics
                posts_count = len(posts)
                total_likes = 0
                total_shares = 0
                total_comments = 0
                clicks = 0
                
                for post in posts:
                    engagement_data = post.get_engagement_data()
                    total_likes += engagement_data.get('likes', 0)
                    total_shares += engagement_data.get('shares', 0) + engagement_data.get('retweets', 0)
                    total_comments += engagement_data.get('comments', 0) + engagement_data.get('replies', 0)
                    clicks += engagement_data.get('clicks', 0)
                
                # Estimate revenue (simplified calculation)
                estimated_revenue = clicks * 0.05  # Assume 5 cents per click
                
                # Update or create analytics record
                analytics = Analytics.query.filter_by(
                    date=target_date,
                    platform=platform
                ).first()
                
                if not analytics:
                    analytics = Analytics(
                        date=target_date,
                        platform=platform
                    )
                    db.session.add(analytics)
                
                analytics.posts_count = posts_count
                analytics.total_likes = total_likes
                analytics.total_shares = total_shares
                analytics.total_comments = total_comments
                analytics.clicks = clicks
                analytics.estimated_revenue = estimated_revenue
                
            db.session.commit()
            logger.info(f"Updated analytics for {target_date}")
            
        except Exception as e:
            logger.error(f"Error updating daily analytics: {e}")
            db.session.rollback()
    
    def get_summary_stats(self, start_date, end_date):
        """Get summary statistics for a date range"""
        try:
            analytics_data = Analytics.query.filter(
                Analytics.date >= start_date,
                Analytics.date <= end_date
            ).all()
            
            total_posts = sum([a.posts_count for a in analytics_data])
            total_likes = sum([a.total_likes for a in analytics_data])
            total_shares = sum([a.total_shares for a in analytics_data])
            total_comments = sum([a.total_comments for a in analytics_data])
            total_clicks = sum([a.clicks for a in analytics_data])
            total_revenue = sum([a.estimated_revenue for a in analytics_data])
            
            # Calculate engagement rate
            total_engagement = total_likes + total_shares + total_comments
            engagement_rate = (total_engagement / total_posts) if total_posts > 0 else 0
            
            # Platform breakdown
            platform_stats = {}
            for platform in ['instagram', 'facebook', 'twitter']:
                platform_data = [a for a in analytics_data if a.platform == platform]
                platform_stats[platform] = {
                    'posts': sum([a.posts_count for a in platform_data]),
                    'likes': sum([a.total_likes for a in platform_data]),
                    'shares': sum([a.total_shares for a in platform_data]),
                    'comments': sum([a.total_comments for a in platform_data]),
                    'clicks': sum([a.clicks for a in platform_data]),
                    'revenue': sum([a.estimated_revenue for a in platform_data])
                }
            
            return {
                'total_posts': total_posts,
                'total_likes': total_likes,
                'total_shares': total_shares,
                'total_comments': total_comments,
                'total_clicks': total_clicks,
                'total_revenue': round(total_revenue, 2),
                'engagement_rate': round(engagement_rate, 2),
                'platform_stats': platform_stats
            }
            
        except Exception as e:
            logger.error(f"Error getting summary stats: {e}")
            return {
                'total_posts': 0,
                'total_likes': 0,
                'total_shares': 0,
                'total_comments': 0,
                'total_clicks': 0,
                'total_revenue': 0,
                'engagement_rate': 0,
                'platform_stats': {}
            }
    
    def prepare_chart_data(self, analytics_data):
        """Prepare data for charts"""
        try:
            # Group data by date
            date_data = {}
            for analytics in analytics_data:
                date_str = analytics.date.strftime('%Y-%m-%d')
                if date_str not in date_data:
                    date_data[date_str] = {
                        'posts': 0,
                        'likes': 0,
                        'shares': 0,
                        'comments': 0,
                        'clicks': 0,
                        'revenue': 0
                    }
                
                date_data[date_str]['posts'] += analytics.posts_count
                date_data[date_str]['likes'] += analytics.total_likes
                date_data[date_str]['shares'] += analytics.total_shares
                date_data[date_str]['comments'] += analytics.total_comments
                date_data[date_str]['clicks'] += analytics.clicks
                date_data[date_str]['revenue'] += analytics.estimated_revenue
            
            # Convert to chart format
            dates = sorted(date_data.keys())
            posts_data = [date_data[date]['posts'] for date in dates]
            engagement_data = [
                date_data[date]['likes'] + date_data[date]['shares'] + date_data[date]['comments']
                for date in dates
            ]
            revenue_data = [round(date_data[date]['revenue'], 2) for date in dates]
            clicks_data = [date_data[date]['clicks'] for date in dates]
            
            # Platform breakdown for pie chart
            platform_data = {'instagram': 0, 'facebook': 0, 'twitter': 0}
            for analytics in analytics_data:
                platform_data[analytics.platform] += (
                    analytics.total_likes + analytics.total_shares + analytics.total_comments
                )
            
            return {
                'dates': dates,
                'posts_data': posts_data,
                'engagement_data': engagement_data,
                'revenue_data': revenue_data,
                'clicks_data': clicks_data,
                'platform_data': platform_data
            }
            
        except Exception as e:
            logger.error(f"Error preparing chart data: {e}")
            return {
                'dates': [],
                'posts_data': [],
                'engagement_data': [],
                'revenue_data': [],
                'clicks_data': [],
                'platform_data': {}
            }
    
    def get_top_performing_products(self, limit=10, days=30):
        """Get top performing products based on engagement"""
        try:
            # Get posts from last N days
            start_date = datetime.now() - timedelta(days=days)
            
            # Query to get products with their engagement metrics
            results = db.session.query(
                Product.id,
                Product.title,
                Product.price,
                Product.image_url,
                func.count(Post.id).label('post_count'),
                func.sum(
                    func.json_extract(Post.engagement_data, '$.likes')
                ).label('total_likes')
            ).join(
                Post, Product.id == Post.product_id
            ).filter(
                Post.created_at >= start_date,
                Post.status == 'posted'
            ).group_by(
                Product.id
            ).order_by(
                func.sum(func.json_extract(Post.engagement_data, '$.likes')).desc()
            ).limit(limit).all()
            
            top_products = []
            for result in results:
                top_products.append({
                    'id': result.id,
                    'title': result.title,
                    'price': result.price,
                    'image_url': result.image_url,
                    'post_count': result.post_count or 0,
                    'total_likes': result.total_likes or 0
                })
            
            return top_products
            
        except Exception as e:
            logger.error(f"Error getting top performing products: {e}")
            return []
    
    def get_platform_performance(self, days=30):
        """Get performance metrics by platform"""
        try:
            start_date = datetime.now().date() - timedelta(days=days)
            
            analytics_data = Analytics.query.filter(
                Analytics.date >= start_date
            ).all()
            
            platform_performance = {}
            
            for platform in ['instagram', 'facebook', 'twitter']:
                platform_data = [a for a in analytics_data if a.platform == platform]
                
                total_posts = sum([a.posts_count for a in platform_data])
                total_engagement = sum([
                    a.total_likes + a.total_shares + a.total_comments 
                    for a in platform_data
                ])
                total_clicks = sum([a.clicks for a in platform_data])
                total_revenue = sum([a.estimated_revenue for a in platform_data])
                
                avg_engagement = (total_engagement / total_posts) if total_posts > 0 else 0
                click_rate = (total_clicks / total_posts) if total_posts > 0 else 0
                
                platform_performance[platform] = {
                    'posts': total_posts,
                    'engagement': total_engagement,
                    'clicks': total_clicks,
                    'revenue': round(total_revenue, 2),
                    'avg_engagement': round(avg_engagement, 2),
                    'click_rate': round(click_rate, 2)
                }
            
            return platform_performance
            
        except Exception as e:
            logger.error(f"Error getting platform performance: {e}")
            return {}
    
    def generate_performance_report(self, days=30):
        """Generate comprehensive performance report"""
        try:
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=days)
            
            # Get summary stats
            summary_stats = self.get_summary_stats(start_date, end_date)
            
            # Get platform performance
            platform_performance = self.get_platform_performance(days)
            
            # Get top products
            top_products = self.get_top_performing_products(limit=5, days=days)
            
            # Calculate trends (compare with previous period)
            prev_start = start_date - timedelta(days=days)
            prev_end = start_date
            prev_stats = self.get_summary_stats(prev_start, prev_end)
            
            # Calculate percentage changes
            trends = {}
            for metric in ['total_posts', 'total_likes', 'total_clicks', 'total_revenue']:
                current_value = summary_stats[metric]
                prev_value = prev_stats[metric]
                
                if prev_value > 0:
                    change = ((current_value - prev_value) / prev_value) * 100
                else:
                    change = 100 if current_value > 0 else 0
                
                trends[metric] = round(change, 1)
            
            report = {
                'period': {
                    'start_date': start_date.strftime('%Y-%m-%d'),
                    'end_date': end_date.strftime('%Y-%m-%d'),
                    'days': days
                },
                'summary_stats': summary_stats,
                'platform_performance': platform_performance,
                'top_products': top_products,
                'trends': trends,
                'generated_at': datetime.now().isoformat()
            }
            
            return report
            
        except Exception as e:
            logger.error(f"Error generating performance report: {e}")
            return {}
    
    def update_all_analytics(self):
        """Update analytics for all recent dates"""
        try:
            # Update last 7 days
            for i in range(7):
                target_date = datetime.now().date() - timedelta(days=i)
                self.update_daily_analytics(target_date)
            
            logger.info("Updated analytics for last 7 days")
            
        except Exception as e:
            logger.error(f"Error updating all analytics: {e}")

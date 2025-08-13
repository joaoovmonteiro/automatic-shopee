from app import db
from datetime import datetime
from sqlalchemy import JSON
import json

class Product(db.Model):
    """Model for Shopee products"""
    id = db.Column(db.Integer, primary_key=True)
    shopee_id = db.Column(db.String(100), unique=True, nullable=False)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    original_price = db.Column(db.Float)
    discount = db.Column(db.Integer, default=0)
    image_url = db.Column(db.String(500))
    category = db.Column(db.String(100))
    rating = db.Column(db.Float, default=0.0)
    sold_count = db.Column(db.Integer, default=0)
    product_url = db.Column(db.String(500))
    affiliate_link = db.Column(db.String(500))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship with posts
    posts = db.relationship('Post', backref='product', lazy=True)

class Post(db.Model):
    """Model for social media posts"""
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    platform = db.Column(db.String(50), nullable=False)  # instagram, facebook, twitter
    content = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='scheduled')  # scheduled, posted, failed
    scheduled_time = db.Column(db.DateTime)
    posted_time = db.Column(db.DateTime)
    post_id = db.Column(db.String(100))  # Platform-specific post ID
    engagement_data = db.Column(JSON)  # Store likes, shares, comments
    error_message = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def get_engagement_data(self):
        """Get engagement data as dict"""
        if self.engagement_data:
            return json.loads(self.engagement_data) if isinstance(self.engagement_data, str) else self.engagement_data
        return {'likes': 0, 'shares': 0, 'comments': 0}

class SocialMediaAccount(db.Model):
    """Model for social media account configurations"""
    id = db.Column(db.Integer, primary_key=True)
    platform = db.Column(db.String(50), unique=True, nullable=False)
    username = db.Column(db.String(100))
    access_token = db.Column(db.String(500))
    refresh_token = db.Column(db.String(500))
    token_expires_at = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ScheduleConfig(db.Model):
    """Model for posting schedule configuration"""
    id = db.Column(db.Integer, primary_key=True)
    platform = db.Column(db.String(50), nullable=False)
    interval_hours = db.Column(db.Integer, default=6)  # Post every X hours
    posting_times = db.Column(JSON)  # Preferred posting times
    is_active = db.Column(db.Boolean, default=True)
    max_posts_per_day = db.Column(db.Integer, default=4)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def get_posting_times(self):
        """Get posting times as list"""
        if self.posting_times:
            return json.loads(self.posting_times) if isinstance(self.posting_times, str) else self.posting_times
        return ['09:00', '14:00', '18:00', '21:00']

class AffiliateConfig(db.Model):
    """Model for affiliate configuration"""
    id = db.Column(db.Integer, primary_key=True)
    affiliate_id = db.Column(db.String(100), nullable=False)
    base_affiliate_url = db.Column(db.String(500), nullable=False)
    commission_rate = db.Column(db.Float, default=5.0)
    tracking_params = db.Column(JSON)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Analytics(db.Model):
    """Model for analytics data"""
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    platform = db.Column(db.String(50), nullable=False)
    posts_count = db.Column(db.Integer, default=0)
    total_likes = db.Column(db.Integer, default=0)
    total_shares = db.Column(db.Integer, default=0)
    total_comments = db.Column(db.Integer, default=0)
    clicks = db.Column(db.Integer, default=0)
    estimated_revenue = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (db.UniqueConstraint('date', 'platform'),)

#!/usr/bin/env python3
"""
Database setup script for Shopee Affiliate Marketing System
Initializes affiliate configuration and social media accounts
"""

import os
from app import app, db
from models import AffiliateConfig, SocialMediaAccount, ScheduleConfig

def setup_database():
    """Initialize database with default configurations"""
    with app.app_context():
        # Create all tables
        db.create_all()
        print("✓ Database tables created")
        
        # Setup affiliate configuration
        setup_affiliate_config()
        
        # Setup social media accounts
        setup_social_media_accounts()
        
        # Setup posting schedules
        setup_posting_schedules()
        
        print("✓ Database setup complete!")

def setup_affiliate_config():
    """Setup affiliate configuration"""
    affiliate_id = os.environ.get("SHOPEE_AFFILIATE_ID")
    
    if not affiliate_id:
        print("⚠️ SHOPEE_AFFILIATE_ID not found in environment variables")
        return
    
    # Check if config already exists
    config = AffiliateConfig.query.first()
    
    if config:
        # Update existing config
        config.affiliate_id = affiliate_id
        config.base_affiliate_url = "https://shopee.com.br"
        config.commission_rate = 5.0
        config.is_active = True
        print(f"✓ Updated affiliate config for ID: {affiliate_id}")
    else:
        # Create new config
        config = AffiliateConfig(
            affiliate_id=affiliate_id,
            base_affiliate_url="https://shopee.com.br",
            commission_rate=5.0,
            is_active=True
        )
        db.session.add(config)
        print(f"✓ Created affiliate config for ID: {affiliate_id}")
    
    db.session.commit()

def setup_social_media_accounts():
    """Setup social media accounts"""
    instagram_username = os.environ.get("INSTAGRAM_USERNAME")
    
    accounts = [
        {
            'platform': 'instagram',
            'username': instagram_username or 'achadinhos_technologia'
        },
        {
            'platform': 'twitter', 
            'username': 'achadinhos_tech'
        }
    ]
    
    for account_data in accounts:
        account = SocialMediaAccount.query.filter_by(
            platform=account_data['platform']
        ).first()
        
        if account:
            # Update existing account
            account.username = account_data['username']
            account.is_active = True
            print(f"✓ Updated {account_data['platform']} account: @{account_data['username']}")
        else:
            # Create new account
            account = SocialMediaAccount(
                platform=account_data['platform'],
                username=account_data['username'],
                is_active=True
            )
            db.session.add(account)
            print(f"✓ Created {account_data['platform']} account: @{account_data['username']}")
    
    db.session.commit()

def setup_posting_schedules():
    """Setup default posting schedules"""
    platforms = ['instagram', 'twitter']
    
    for platform in platforms:
        schedule = ScheduleConfig.query.filter_by(platform=platform).first()
        
        schedule_data = {
            'platform': platform,
            'interval_hours': 4,  # Post every 4 hours
            'max_posts_per_day': 6,
            'posting_times': ['09:00', '13:00', '17:00', '21:00'],
            'is_active': True
        }
        
        if schedule:
            # Update existing schedule
            for key, value in schedule_data.items():
                if key != 'platform':
                    setattr(schedule, key, value)
            print(f"✓ Updated posting schedule for {platform}")
        else:
            # Create new schedule
            schedule = ScheduleConfig(**schedule_data)
            db.session.add(schedule)
            print(f"✓ Created posting schedule for {platform}")
    
    db.session.commit()

if __name__ == "__main__":
    setup_database()
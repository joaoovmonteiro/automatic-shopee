import logging
from datetime import datetime, timedelta
from app import app, scheduler, db
from models import ScheduleConfig, Product, Post, SocialMediaAccount
from services.social_media_service import SocialMediaService
from services.shopee_service import ShopeeService
import random

logger = logging.getLogger(__name__)

class SchedulerService:
    """Service for handling post scheduling"""
    
    def __init__(self):
        self.social_media_service = SocialMediaService()
        self.shopee_service = ShopeeService()
    
    def initialize_schedules(self):
        """Initialize default schedules for all platforms"""
        try:
            with app.app_context():
                platforms = ['instagram', 'facebook', 'twitter']
                
                for platform in platforms:
                    schedule = ScheduleConfig.query.filter_by(platform=platform).first()
                    if not schedule:
                        schedule = ScheduleConfig(
                            platform=platform,
                            interval_hours=6,
                            max_posts_per_day=4,
                            posting_times=['09:00', '14:00', '18:00', '21:00'],
                            is_active=True
                        )
                        db.session.add(schedule)
                
                db.session.commit()
                
                # Start scheduling for all platforms
                for platform in platforms:
                    self.schedule_posts_for_platform(platform)
                
                logger.info("Initialized schedules for all platforms")
                
        except Exception as e:
            logger.error(f"Error initializing schedules: {e}")
    
    def schedule_posts_for_platform(self, platform):
        """Schedule automated posts for a specific platform"""
        try:
            with app.app_context():
                # Remove existing jobs for this platform
                job_id = f"auto_post_{platform}"
                try:
                    scheduler.remove_job(job_id)
                except:
                    pass  # Job doesn't exist
                
                # Get schedule configuration
                schedule_config = ScheduleConfig.query.filter_by(
                    platform=platform, 
                    is_active=True
                ).first()
                
                if not schedule_config:
                    logger.warning(f"No active schedule config found for {platform}")
                    return False
                
                # Check if account is configured
                account = SocialMediaAccount.query.filter_by(
                    platform=platform, 
                    is_active=True
                ).first()
                
                if not account:
                    logger.warning(f"No active account found for {platform}")
                    return False
                
                # Schedule posts based on interval
                scheduler.add_job(
                    id=job_id,
                    func=self.create_scheduled_post,
                    trigger='interval',
                    hours=schedule_config.interval_hours,
                    args=[platform],
                    next_run_time=datetime.now() + timedelta(minutes=1)  # Start in 1 minute
                )
                
                logger.info(f"Scheduled posts for {platform} every {schedule_config.interval_hours} hours")
                return True
                
        except Exception as e:
            logger.error(f"Error scheduling posts for {platform}: {e}")
            return False
    
    def create_scheduled_post(self, platform):
        """Create a scheduled post for a platform"""
        try:
            with app.app_context():
                # Check daily post limit
                today = datetime.now().date()
                today_posts = Post.query.filter(
                    Post.platform == platform,
                    db.func.date(Post.created_at) == today
                ).count()
                
                schedule_config = ScheduleConfig.query.filter_by(platform=platform).first()
                max_posts = schedule_config.max_posts_per_day if schedule_config else 4
                
                if today_posts >= max_posts:
                    logger.info(f"Daily post limit reached for {platform} ({today_posts}/{max_posts})")
                    return
                
                # Get a trending product for posting
                products = self.shopee_service.get_trending_products_for_posting(limit=10)
                
                if not products:
                    logger.warning(f"No products available for posting on {platform}")
                    return
                
                # Select a random product that hasn't been posted recently
                recent_product_ids = [
                    p.product_id for p in Post.query.filter(
                        Post.platform == platform,
                        Post.created_at >= datetime.now() - timedelta(days=7)
                    ).all()
                ]
                
                available_products = [p for p in products if p.id not in recent_product_ids]
                
                if not available_products:
                    available_products = products  # Use any product if all were posted recently
                
                selected_product = random.choice(available_products)
                
                # Create the post
                success = self.social_media_service.create_post(
                    selected_product, 
                    platform
                )
                
                if success:
                    logger.info(f"Successfully created scheduled post for {platform}: {selected_product.title}")
                else:
                    logger.error(f"Failed to create scheduled post for {platform}")
                    
        except Exception as e:
            logger.error(f"Error creating scheduled post for {platform}: {e}")
    
    def schedule_specific_post(self, product_id, platform, scheduled_time):
        """Schedule a specific post for a specific time"""
        try:
            with app.app_context():
                product = Product.query.get(product_id)
                if not product:
                    logger.error(f"Product {product_id} not found")
                    return False
                
                # Create post record with scheduled time
                success = self.social_media_service.create_post(
                    product, 
                    platform, 
                    scheduled_time=scheduled_time
                )
                
                if success:
                    # Schedule the actual posting job
                    job_id = f"post_{product_id}_{platform}_{int(scheduled_time.timestamp())}"
                    
                    scheduler.add_job(
                        id=job_id,
                        func=self.execute_scheduled_post,
                        trigger='date',
                        run_date=scheduled_time,
                        args=[product_id, platform]
                    )
                    
                    logger.info(f"Scheduled specific post for {platform} at {scheduled_time}")
                    return True
                
                return False
                
        except Exception as e:
            logger.error(f"Error scheduling specific post: {e}")
            return False
    
    def execute_scheduled_post(self, product_id, platform):
        """Execute a scheduled post"""
        try:
            with app.app_context():
                # Find the scheduled post
                post = Post.query.filter_by(
                    product_id=product_id,
                    platform=platform,
                    status='scheduled'
                ).order_by(Post.created_at.desc()).first()
                
                if not post:
                    logger.error(f"Scheduled post not found for product {product_id} on {platform}")
                    return
                
                # Get account
                account = SocialMediaAccount.query.filter_by(
                    platform=platform, 
                    is_active=True
                ).first()
                
                if not account:
                    post.status = 'failed'
                    post.error_message = f"No active account found for {platform}"
                    db.session.commit()
                    return
                
                # Execute the post
                success = self.social_media_service.simulate_post_to_platform(post, account)
                
                if success:
                    post.status = 'posted'
                    post.posted_time = datetime.utcnow()
                    post.post_id = f"{platform}_{random.randint(1000000, 9999999)}"
                    post.engagement_data = self.social_media_service.generate_simulated_engagement(platform)
                else:
                    post.status = 'failed'
                    post.error_message = "Failed to post to platform"
                
                db.session.commit()
                logger.info(f"Executed scheduled post: {post.id}")
                
        except Exception as e:
            logger.error(f"Error executing scheduled post: {e}")
    
    def pause_platform_scheduling(self, platform):
        """Pause scheduling for a platform"""
        try:
            job_id = f"auto_post_{platform}"
            scheduler.pause_job(job_id)
            logger.info(f"Paused scheduling for {platform}")
            return True
        except Exception as e:
            logger.error(f"Error pausing scheduling for {platform}: {e}")
            return False
    
    def resume_platform_scheduling(self, platform):
        """Resume scheduling for a platform"""
        try:
            job_id = f"auto_post_{platform}"
            scheduler.resume_job(job_id)
            logger.info(f"Resumed scheduling for {platform}")
            return True
        except Exception as e:
            logger.error(f"Error resuming scheduling for {platform}: {e}")
            return False
    
    def get_scheduled_jobs(self):
        """Get all scheduled jobs"""
        try:
            jobs = scheduler.get_jobs()
            job_info = []
            
            for job in jobs:
                job_info.append({
                    'id': job.id,
                    'name': job.name,
                    'next_run_time': job.next_run_time,
                    'trigger': str(job.trigger)
                })
            
            return job_info
        except Exception as e:
            logger.error(f"Error getting scheduled jobs: {e}")
            return []
    
    def cancel_scheduled_post(self, post_id):
        """Cancel a scheduled post"""
        try:
            with app.app_context():
                post = Post.query.get(post_id)
                if not post or post.status != 'scheduled':
                    return False
                
                # Remove from scheduler if it has a job
                job_id = f"post_{post.product_id}_{post.platform}_{int(post.scheduled_time.timestamp())}"
                try:
                    scheduler.remove_job(job_id)
                except:
                    pass  # Job doesn't exist or already executed
                
                # Update post status
                post.status = 'cancelled'
                db.session.commit()
                
                logger.info(f"Cancelled scheduled post: {post_id}")
                return True
                
        except Exception as e:
            logger.error(f"Error cancelling scheduled post: {e}")
            return False
    
    def update_engagement_data(self):
        """Update engagement data for recent posts"""
        try:
            with app.app_context():
                # Get posts from last 30 days
                recent_posts = Post.query.filter(
                    Post.status == 'posted',
                    Post.posted_time >= datetime.now() - timedelta(days=30)
                ).all()
                
                updated_count = 0
                for post in recent_posts:
                    if self.social_media_service.update_post_engagement(post.id):
                        updated_count += 1
                
                logger.info(f"Updated engagement data for {updated_count} posts")
                return updated_count
                
        except Exception as e:
            logger.error(f"Error updating engagement data: {e}")
            return 0

# Initialize scheduler when module is imported
scheduler_service = SchedulerService()

# Schedule engagement data updates every hour
with app.app_context():
    try:
        scheduler.add_job(
            id='update_engagement',
            func=scheduler_service.update_engagement_data,
            trigger='interval',
            hours=1,
            next_run_time=datetime.now() + timedelta(minutes=5)
        )
        logger.info("Scheduled engagement data updates")
    except Exception as e:
        logger.error(f"Error scheduling engagement updates: {e}")

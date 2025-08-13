from flask import render_template, request, jsonify, redirect, url_for, flash
from app import app, db
from models import Product, Post, SocialMediaAccount, ScheduleConfig, AffiliateConfig, Analytics
from services.shopee_service import ShopeeService
from services.social_media_service import SocialMediaService
from services.scheduler_service import SchedulerService
from services.analytics_service import AnalyticsService
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

# Initialize services
shopee_service = ShopeeService()
social_media_service = SocialMediaService()
scheduler_service = SchedulerService()
analytics_service = AnalyticsService()

@app.route('/')
def dashboard():
    """Main dashboard view"""
    try:
        # Get recent statistics
        total_products = Product.query.filter_by(is_active=True).count()
        total_posts = Post.query.count()
        recent_posts = Post.query.order_by(Post.created_at.desc()).limit(5).all()
        
        # Get today's analytics
        today = datetime.now().date()
        today_analytics = Analytics.query.filter_by(date=today).all()
        
        # Calculate totals for today
        today_stats = {
            'posts': sum([a.posts_count for a in today_analytics]),
            'likes': sum([a.total_likes for a in today_analytics]),
            'shares': sum([a.total_shares for a in today_analytics]),
            'clicks': sum([a.clicks for a in today_analytics])
        }
        
        # Get scheduled posts count
        scheduled_posts = Post.query.filter_by(status='scheduled').count()
        
        return render_template('dashboard.html',
                             total_products=total_products,
                             total_posts=total_posts,
                             recent_posts=recent_posts,
                             today_stats=today_stats,
                             scheduled_posts=scheduled_posts)
    except Exception as e:
        logger.error(f"Dashboard error: {e}")
        return render_template('dashboard.html',
                             total_products=0,
                             total_posts=0,
                             recent_posts=[],
                             today_stats={'posts': 0, 'likes': 0, 'shares': 0, 'clicks': 0},
                             scheduled_posts=0)

@app.route('/products')
def products():
    """Products management view"""
    page = request.args.get('page', 1, type=int)
    category = request.args.get('category', '')
    search = request.args.get('search', '')
    
    query = Product.query.filter_by(is_active=True)
    
    if category:
        query = query.filter(Product.category == category)
    
    if search:
        query = query.filter(Product.title.contains(search))
    
    products = query.order_by(Product.created_at.desc()).paginate(
        page=page, per_page=12, error_out=False)
    
    categories = db.session.query(Product.category).distinct().all()
    categories = [cat[0] for cat in categories if cat[0]]
    
    return render_template('products.html', 
                         products=products, 
                         categories=categories,
                         current_category=category,
                         current_search=search)

@app.route('/refresh_products')
def refresh_products():
    """Refresh products from Shopee"""
    try:
        new_products = shopee_service.fetch_trending_products()
        flash(f'Successfully added {len(new_products)} new products!', 'success')
    except Exception as e:
        logger.error(f"Error refreshing products: {e}")
        flash('Error refreshing products. Please try again.', 'error')
    
    return redirect(url_for('products'))

@app.route('/schedule')
def schedule():
    """Schedule management view"""
    schedules = ScheduleConfig.query.all()
    scheduled_posts = Post.query.filter_by(status='scheduled').order_by(Post.scheduled_time).all()
    
    return render_template('schedule.html', 
                         schedules=schedules, 
                         scheduled_posts=scheduled_posts)

@app.route('/update_schedule', methods=['POST'])
def update_schedule():
    """Update schedule configuration"""
    try:
        platform = request.form.get('platform')
        interval_hours = int(request.form.get('interval_hours', 6))
        max_posts_per_day = int(request.form.get('max_posts_per_day', 4))
        posting_times = request.form.getlist('posting_times[]')
        
        schedule = ScheduleConfig.query.filter_by(platform=platform).first()
        if not schedule:
            schedule = ScheduleConfig(platform=platform)
            db.session.add(schedule)
        
        schedule.interval_hours = interval_hours
        schedule.max_posts_per_day = max_posts_per_day
        schedule.posting_times = posting_times
        schedule.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        # Restart scheduler for this platform
        scheduler_service.schedule_posts_for_platform(platform)
        
        flash(f'Schedule updated for {platform}!', 'success')
    except Exception as e:
        logger.error(f"Error updating schedule: {e}")
        flash('Error updating schedule. Please try again.', 'error')
    
    return redirect(url_for('schedule'))

@app.route('/history')
def history():
    """Post history view"""
    page = request.args.get('page', 1, type=int)
    platform = request.args.get('platform', '')
    status = request.args.get('status', '')
    
    query = Post.query
    
    if platform:
        query = query.filter(Post.platform == platform)
    
    if status:
        query = query.filter(Post.status == status)
    
    posts = query.order_by(Post.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False)
    
    platforms = ['instagram', 'facebook', 'twitter']
    statuses = ['scheduled', 'posted', 'failed']
    
    return render_template('history.html', 
                         posts=posts, 
                         platforms=platforms,
                         statuses=statuses,
                         current_platform=platform,
                         current_status=status)

@app.route('/analytics')
def analytics():
    """Analytics dashboard view"""
    # Get date range from request
    days = request.args.get('days', 7, type=int)
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=days)
    
    # Get analytics data
    analytics_data = Analytics.query.filter(
        Analytics.date >= start_date,
        Analytics.date <= end_date
    ).order_by(Analytics.date).all()
    
    # Prepare data for charts
    chart_data = analytics_service.prepare_chart_data(analytics_data)
    
    # Get summary statistics
    summary_stats = analytics_service.get_summary_stats(start_date, end_date)
    
    return render_template('analytics.html', 
                         chart_data=chart_data,
                         summary_stats=summary_stats,
                         days=days)

@app.route('/settings')
def settings():
    """Settings view"""
    social_accounts = SocialMediaAccount.query.all()
    affiliate_config = AffiliateConfig.query.first()
    
    if not affiliate_config:
        affiliate_config = AffiliateConfig(
            affiliate_id='',
            base_affiliate_url='https://shopee.com.br/',
            commission_rate=5.0
        )
    
    return render_template('settings.html', 
                         social_accounts=social_accounts,
                         affiliate_config=affiliate_config)

@app.route('/update_settings', methods=['POST'])
def update_settings():
    """Update system settings"""
    try:
        # Update affiliate configuration
        affiliate_id = request.form.get('affiliate_id')
        base_affiliate_url = request.form.get('base_affiliate_url')
        commission_rate = float(request.form.get('commission_rate', 5.0))
        
        affiliate_config = AffiliateConfig.query.first()
        if not affiliate_config:
            affiliate_config = AffiliateConfig()
            db.session.add(affiliate_config)
        
        affiliate_config.affiliate_id = affiliate_id
        affiliate_config.base_affiliate_url = base_affiliate_url
        affiliate_config.commission_rate = commission_rate
        affiliate_config.updated_at = datetime.utcnow()
        
        # Update social media accounts
        for platform in ['instagram', 'facebook', 'twitter']:
            username = request.form.get(f'{platform}_username')
            access_token = request.form.get(f'{platform}_access_token')
            
            if username and access_token:
                account = SocialMediaAccount.query.filter_by(platform=platform).first()
                if not account:
                    account = SocialMediaAccount(platform=platform)
                    db.session.add(account)
                
                account.username = username
                account.access_token = access_token
                account.updated_at = datetime.utcnow()
        
        db.session.commit()
        flash('Settings updated successfully!', 'success')
    except Exception as e:
        logger.error(f"Error updating settings: {e}")
        flash('Error updating settings. Please try again.', 'error')
    
    return redirect(url_for('settings'))

@app.route('/api/post_now/<int:product_id>')
def post_now(product_id):
    """Create immediate post for a product"""
    try:
        product = Product.query.get_or_404(product_id)
        
        # Create posts for all active platforms
        active_accounts = SocialMediaAccount.query.filter_by(is_active=True).all()
        posts_created = 0
        
        for account in active_accounts:
            success = social_media_service.create_post(product, account.platform)
            if success:
                posts_created += 1
        
        return jsonify({
            'success': True, 
            'message': f'Created {posts_created} posts for {product.title}'
        })
    except Exception as e:
        logger.error(f"Error creating immediate post: {e}")
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/toggle_product/<int:product_id>')
def toggle_product(product_id):
    """Toggle product active status"""
    try:
        product = Product.query.get_or_404(product_id)
        product.is_active = not product.is_active
        db.session.commit()
        
        return jsonify({
            'success': True, 
            'is_active': product.is_active
        })
    except Exception as e:
        logger.error(f"Error toggling product: {e}")
        return jsonify({'success': False, 'message': str(e)})

@app.errorhandler(404)
def not_found_error(error):
    return render_template('dashboard.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('dashboard.html'), 500

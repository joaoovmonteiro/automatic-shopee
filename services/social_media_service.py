import logging
import random
from datetime import datetime, timedelta
from app import db
from models import Post, SocialMediaAccount, Product
import json

logger = logging.getLogger(__name__)

class SocialMediaService:
    """Service for handling social media operations"""
    
    def __init__(self):
        self.platforms = {
            'instagram': {
                'max_chars': 2200,
                'hashtag_limit': 30,
                'supports_images': True
            },
            'facebook': {
                'max_chars': 63206,
                'hashtag_limit': 5,
                'supports_images': True
            },
            'twitter': {
                'max_chars': 280,
                'hashtag_limit': 10,
                'supports_images': True
            }
        }
    
    def create_post(self, product, platform, scheduled_time=None):
        """Create a social media post for a product"""
        try:
            # Check if platform is configured
            account = SocialMediaAccount.query.filter_by(
                platform=platform, 
                is_active=True
            ).first()
            
            if not account:
                logger.warning(f"No active account found for platform: {platform}")
                return False
            
            # Generate post content
            content = self.generate_post_content(product, platform)
            
            # Create post record
            post = Post(
                product_id=product.id,
                platform=platform,
                content=content,
                scheduled_time=scheduled_time or datetime.utcnow(),
                status='scheduled' if scheduled_time else 'posted'
            )
            
            # If posting immediately, simulate the posting process
            if not scheduled_time:
                success = self.simulate_post_to_platform(post, account)
                if success:
                    post.status = 'posted'
                    post.posted_time = datetime.utcnow()
                    post.post_id = f"{platform}_{random.randint(1000000, 9999999)}"
                    
                    # Generate simulated engagement data
                    post.engagement_data = json.dumps(self.generate_simulated_engagement(platform))
                else:
                    post.status = 'failed'
                    post.error_message = "Simulated posting failure"
            
            db.session.add(post)
            db.session.commit()
            
            logger.info(f"Created {platform} post for product: {product.title}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating post for {platform}: {e}")
            db.session.rollback()
            return False
    
    def generate_post_content(self, product, platform):
        """Generate optimized content for each platform"""
        try:
            platform_config = self.platforms.get(platform, {})
            max_chars = platform_config.get('max_chars', 280)
            
            # Base content elements
            title = product.title
            price = f"R$ {product.price:.2f}"
            discount_text = f"{product.discount}% OFF" if product.discount > 0 else ""
            link = product.affiliate_link
            
            # Platform-specific content generation
            if platform == 'instagram':
                content = self.generate_instagram_content(product, title, price, discount_text, link)
            elif platform == 'facebook':
                content = self.generate_facebook_content(product, title, price, discount_text, link)
            elif platform == 'twitter':
                content = self.generate_twitter_content(product, title, price, discount_text, link)
            else:
                content = f"{title}\n{discount_text} {price}\n{link}"
            
            # Truncate if necessary
            if len(content) > max_chars:
                content = content[:max_chars-3] + "..."
            
            return content
            
        except Exception as e:
            logger.error(f"Error generating content for {platform}: {e}")
            return f"{product.title}\nR$ {product.price:.2f}\n{product.affiliate_link}"
    
    def generate_instagram_content(self, product, title, price, discount_text, link):
        """Generate Instagram-optimized content"""
        emojis = ["🔥", "⚡", "💎", "✨", "🎯", "🛍️", "💯", "🚀"]
        selected_emoji = random.choice(emojis)
        
        hashtags = self.generate_hashtags(product.category, platform='instagram')
        
        content = f"""{selected_emoji} {title}

{discount_text} por apenas {price}!

📦 Entrega rápida
⭐ Avaliação: {product.rating}/5.0
👥 Mais de {product.sold_count} vendidos

{link}

{hashtags}"""
        
        return content
    
    def generate_facebook_content(self, product, title, price, discount_text, link):
        """Generate Facebook-optimized content"""
        content = f"""🛍️ OFERTA ESPECIAL: {title}

{discount_text if discount_text else 'Preço imperdível'}: {price}

✅ {product.description}

⭐ Avaliação dos clientes: {product.rating}/5.0
📊 Mais de {product.sold_count} pessoas já compraram

🚚 Frete grátis disponível
💳 Parcelamento sem juros

Aproveite essa oportunidade única! 👇
{link}

#{product.category.replace(' ', '')} #ShopeeOficial #PromoçãoImperdível"""
        
        return content
    
    def generate_twitter_content(self, product, title, price, discount_text, link):
        """Generate Twitter-optimized content"""
        # Shorter content for Twitter
        short_title = title[:100] + "..." if len(title) > 100 else title
        hashtags = self.generate_hashtags(product.category, platform='twitter', limit=3)
        
        content = f"🔥 {short_title}\n{discount_text} {price}\n⭐ {product.rating}/5\n{link}\n{hashtags}"
        
        return content
    
    def generate_hashtags(self, category, platform='instagram', limit=None):
        """Generate relevant hashtags for the category"""
        hashtag_map = {
            'Eletrônicos': ['#eletronicos', '#tech', '#tecnologia', '#gadgets', '#smartphone', '#eletrônicos'],
            'Moda Feminina': ['#modafeminina', '#fashion', '#estilo', '#moda', '#lookdodia', '#outfit'],
            'Moda Masculina': ['#modamasculina', '#mensfashion', '#style', '#masculino', '#moda', '#streetwear'],
            'Casa e Jardim': ['#casaedecoração', '#home', '#decoração', '#casa', '#homedecor', '#organização'],
            'Beleza e Cuidados': ['#beleza', '#skincare', '#makeup', '#beauty', '#cuidados', '#cosméticos'],
            'Esportes': ['#esportes', '#fitness', '#treino', '#academia', '#sport', '#workout'],
            'Brinquedos': ['#brinquedos', '#kids', '#criancas', '#toys', '#infantil', '#diversão'],
            'Pets': ['#pets', '#cachorro', '#gato', '#petshop', '#animais', '#petlovers']
        }
        
        base_hashtags = ['#ofertas', '#promoção', '#desconto', '#shopee', '#compraonline']
        category_hashtags = hashtag_map.get(category, [])
        
        all_hashtags = category_hashtags + base_hashtags
        
        # Platform-specific limits
        if limit is None:
            limit = self.platforms.get(platform, {}).get('hashtag_limit', 10)
        
        selected_hashtags = random.sample(all_hashtags, min(len(all_hashtags), limit))
        return ' '.join(selected_hashtags)
    
    def simulate_post_to_platform(self, post, account):
        """Simulate posting to social media platform"""
        try:
            # Simulate API call with random success/failure
            success_rate = 0.9  # 90% success rate
            
            if random.random() < success_rate:
                logger.info(f"Successfully posted to {post.platform} for account {account.username}")
                return True
            else:
                logger.warning(f"Failed to post to {post.platform} for account {account.username}")
                return False
                
        except Exception as e:
            logger.error(f"Error simulating post to {post.platform}: {e}")
            return False
    
    def generate_simulated_engagement(self, platform):
        """Generate simulated engagement data"""
        # Different engagement patterns for different platforms
        if platform == 'instagram':
            return {
                'likes': random.randint(10, 500),
                'comments': random.randint(0, 25),
                'shares': random.randint(0, 15),
                'saves': random.randint(0, 30)
            }
        elif platform == 'facebook':
            return {
                'likes': random.randint(5, 200),
                'comments': random.randint(0, 15),
                'shares': random.randint(0, 50),
                'reactions': random.randint(0, 30)
            }
        elif platform == 'twitter':
            return {
                'likes': random.randint(0, 100),
                'retweets': random.randint(0, 25),
                'replies': random.randint(0, 10),
                'clicks': random.randint(5, 100)
            }
        else:
            return {
                'likes': random.randint(0, 50),
                'shares': random.randint(0, 10),
                'comments': random.randint(0, 5)
            }
    
    def update_post_engagement(self, post_id):
        """Update engagement data for a post"""
        try:
            post = Post.query.get(post_id)
            if not post or post.status != 'posted':
                return False
            
            # Simulate updated engagement data
            current_engagement = post.get_engagement_data()
            
            # Slightly increase engagement numbers
            for key, value in current_engagement.items():
                if random.random() < 0.3:  # 30% chance to increase
                    current_engagement[key] = value + random.randint(1, 5)
            
            post.engagement_data = json.dumps(current_engagement)
            db.session.commit()
            
            return True
            
        except Exception as e:
            logger.error(f"Error updating post engagement: {e}")
            return False
    
    def get_platform_posts(self, platform, limit=10):
        """Get recent posts for a specific platform"""
        try:
            posts = Post.query.filter_by(platform=platform).order_by(
                Post.created_at.desc()
            ).limit(limit).all()
            
            return posts
            
        except Exception as e:
            logger.error(f"Error getting posts for platform {platform}: {e}")
            return []
    
    def retry_failed_posts(self):
        """Retry failed posts"""
        try:
            failed_posts = Post.query.filter_by(status='failed').all()
            retried_count = 0
            
            for post in failed_posts:
                account = SocialMediaAccount.query.filter_by(
                    platform=post.platform, 
                    is_active=True
                ).first()
                
                if account:
                    success = self.simulate_post_to_platform(post, account)
                    if success:
                        post.status = 'posted'
                        post.posted_time = datetime.utcnow()
                        post.post_id = f"{post.platform}_{random.randint(1000000, 9999999)}"
                        post.engagement_data = json.dumps(self.generate_simulated_engagement(post.platform))
                        post.error_message = None
                        retried_count += 1
            
            if retried_count > 0:
                db.session.commit()
                logger.info(f"Successfully retried {retried_count} failed posts")
            
            return retried_count
            
        except Exception as e:
            logger.error(f"Error retrying failed posts: {e}")
            return 0

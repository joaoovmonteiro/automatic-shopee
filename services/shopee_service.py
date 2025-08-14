import logging
import random
from datetime import datetime
from app import db
from models import Product, AffiliateConfig

logger = logging.getLogger(__name__)

class ShopeeService:
    """Service for handling Shopee product operations"""
    
    def __init__(self):
        self.categories = [
            'Eletrônicos', 'Moda Feminina', 'Moda Masculina', 'Casa e Jardim',
            'Beleza e Cuidados', 'Esportes', 'Livros e Hobbies', 'Brinquedos',
            'Automóveis', 'Saúde', 'Comida e Bebidas', 'Pets'
        ]
    
    def fetch_trending_products(self, limit=20):
        """Fetch trending products from Shopee (simulated with realistic data)"""
        try:
            products = []
            
            # Generate realistic product data
            product_templates = [
                {
                    'title': 'Fone de Ouvido Bluetooth Sem Fio TWS Esportivo',
                    'base_price': 89.90,
                    'category': 'Eletrônicos',
                    'description': 'Fone de ouvido bluetooth 5.0 com cancelamento de ruído, resistente à água IPX5, bateria de longa duração.'
                },
                {
                    'title': 'Vestido Feminino Longo Estampado Verão',
                    'base_price': 69.90,
                    'category': 'Moda Feminina',
                    'description': 'Vestido longo estampado, tecido leve e confortável, ideal para o verão. Diversos tamanhos disponíveis.'
                },
                {
                    'title': 'Tênis Masculino Esportivo Caminhada Corrida',
                    'base_price': 129.90,
                    'category': 'Moda Masculina',
                    'description': 'Tênis esportivo com tecnologia de absorção de impacto, ideal para caminhada e corrida.'
                },
                {
                    'title': 'Conjunto de Panelas Antiaderente 5 Peças',
                    'base_price': 199.90,
                    'category': 'Casa e Jardim',
                    'description': 'Conjunto de panelas antiaderente com revestimento cerâmico, livre de PFOA, cabo ergonômico.'
                },
                {
                    'title': 'Kit Skincare Facial Completo Anti-idade',
                    'base_price': 159.90,
                    'category': 'Beleza e Cuidados',
                    'description': 'Kit completo para cuidados faciais com ácido hialurônico, vitamina C e protetor solar.'
                },
                {
                    'title': 'Smartwatch Fitness Tracker Frequência Cardíaca',
                    'base_price': 249.90,
                    'category': 'Eletrônicos',
                    'description': 'Relógio inteligente com monitor cardíaco, GPS, resistente à água, compatível iOS/Android.'
                },
                {
                    'title': 'Blusa Feminina Manga Longa Social Trabalho',
                    'base_price': 49.90,
                    'category': 'Moda Feminina',
                    'description': 'Blusa social feminina, tecido de qualidade, corte moderno, ideal para ambiente de trabalho.'
                },
                {
                    'title': 'Suporte Para Notebook Ergonômico Ajustável',
                    'base_price': 79.90,
                    'category': 'Eletrônicos',
                    'description': 'Suporte ergonômico para notebook, altura e ângulo ajustáveis, alumínio resistente.'
                }
            ]
            
            for i in range(limit):
                template = random.choice(product_templates)
                
                # Generate unique variations
                shopee_id = f"SP{random.randint(1000000, 9999999)}"
                
                # Check if product already exists
                existing = Product.query.filter_by(shopee_id=shopee_id).first()
                if existing:
                    continue
                
                # Calculate discount and prices
                discount = random.randint(5, 50)
                original_price = template['base_price'] + random.uniform(-20, 50)
                price = original_price * (1 - discount / 100)
                
                # Generate product data
                product_data = {
                    'shopee_id': shopee_id,
                    'title': f"{template['title']} - Modelo {i+1}",
                    'description': template['description'],
                    'price': round(price, 2),
                    'original_price': round(original_price, 2),
                    'discount': discount,
                    'category': template['category'],
                    'rating': round(random.uniform(4.0, 5.0), 1),
                    'sold_count': random.randint(100, 5000),
                    'image_url': self.get_product_image_url(template['category'], i+1),
                    'product_url': f"https://shopee.com.br/product/{shopee_id}",
                    'affiliate_link': self.generate_affiliate_link(shopee_id)
                }
                
                # Create and save product
                product = Product(**product_data)
                db.session.add(product)
                products.append(product)
            
            db.session.commit()
            logger.info(f"Successfully fetched {len(products)} trending products")
            return products
            
        except Exception as e:
            logger.error(f"Error fetching trending products: {e}")
            db.session.rollback()
            return []
    
    def generate_affiliate_link(self, shopee_id):
        """Generate affiliate link for a product"""
        try:
            affiliate_config = AffiliateConfig.query.first()
            if not affiliate_config or not affiliate_config.affiliate_id:
                return f"https://shopee.com.br/product/{shopee_id}"
            
            base_url = affiliate_config.base_affiliate_url.rstrip('/')
            affiliate_id = affiliate_config.affiliate_id
            
            # Generate affiliate link with tracking parameters
            affiliate_link = f"{base_url}/product/{shopee_id}?af={affiliate_id}&pid=partner&c=affiliate"
            
            return affiliate_link
            
        except Exception as e:
            logger.error(f"Error generating affiliate link: {e}")
            return f"https://shopee.com.br/product/{shopee_id}"
    
    def update_product_affiliate_links(self):
        """Update all product affiliate links"""
        try:
            products = Product.query.filter_by(is_active=True).all()
            updated_count = 0
            
            for product in products:
                new_link = self.generate_affiliate_link(product.shopee_id)
                if new_link != product.affiliate_link:
                    product.affiliate_link = new_link
                    product.updated_at = datetime.utcnow()
                    updated_count += 1
            
            if updated_count > 0:
                db.session.commit()
                logger.info(f"Updated affiliate links for {updated_count} products")
            
            return updated_count
            
        except Exception as e:
            logger.error(f"Error updating affiliate links: {e}")
            db.session.rollback()
            return 0
    
    def get_product_image_url(self, category, product_num):
        """Generate reliable product image URLs based on category"""
        # Use multiple image sources for better reliability
        category_images = {
            'Eletrônicos': [
                'https://images.unsplash.com/photo-1498049794561-7780e7231661?w=300&h=300&fit=crop&crop=center',
                'https://images.unsplash.com/photo-1484704849700-f032a568e944?w=300&h=300&fit=crop&crop=center',
                'https://images.unsplash.com/photo-1560472354-b33ff0c44a43?w=300&h=300&fit=crop&crop=center',
                'https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=300&h=300&fit=crop&crop=center',
                'https://images.unsplash.com/photo-1583394838336-acd977736f90?w=300&h=300&fit=crop&crop=center'
            ],
            'Moda Feminina': [
                'https://images.unsplash.com/photo-1515372039744-b8f02a3ae446?w=300&h=300&fit=crop&crop=center',
                'https://images.unsplash.com/photo-1594633312681-425c7b97ccd1?w=300&h=300&fit=crop&crop=center',
                'https://images.unsplash.com/photo-1581338834647-b0fb40704e21?w=300&h=300&fit=crop&crop=center',
                'https://images.unsplash.com/photo-1596755094514-f87e34085b2c?w=300&h=300&fit=crop&crop=center',
                'https://images.unsplash.com/photo-1434389677669-e08b4cac3105?w=300&h=300&fit=crop&crop=center'
            ],
            'Moda Masculina': [
                'https://images.unsplash.com/photo-1603252109612-ffd69d493909?w=300&h=300&fit=crop&crop=center',
                'https://images.unsplash.com/photo-1618886614638-80e3c103d31a?w=300&h=300&fit=crop&crop=center',
                'https://images.unsplash.com/photo-1594938298603-c8148c4dae35?w=300&h=300&fit=crop&crop=center',
                'https://images.unsplash.com/photo-1586790170083-2f9ceadc732d?w=300&h=300&fit=crop&crop=center',
                'https://images.unsplash.com/photo-1607345366928-199ea26cfe3e?w=300&h=300&fit=crop&crop=center'
            ],
            'Casa e Jardim': [
                'https://images.unsplash.com/photo-1586023492125-27b2c045efd7?w=300&h=300&fit=crop&crop=center',
                'https://images.unsplash.com/photo-1567016432779-094069958ea5?w=300&h=300&fit=crop&crop=center',
                'https://images.unsplash.com/photo-1555041469-a586c61ea9bc?w=300&h=300&fit=crop&crop=center',
                'https://images.unsplash.com/photo-1564078516393-cf04bd966897?w=300&h=300&fit=crop&crop=center',
                'https://images.unsplash.com/photo-1558618047-3c8c76ca7f09?w=300&h=300&fit=crop&crop=center'
            ],
            'Beleza e Cuidados': [
                'https://images.unsplash.com/photo-1596462502278-27bfdc403348?w=300&h=300&fit=crop&crop=center',
                'https://images.unsplash.com/photo-1522335789203-aabd1fc54bc9?w=300&h=300&fit=crop&crop=center',
                'https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?w=300&h=300&fit=crop&crop=center',
                'https://images.unsplash.com/photo-1487522794836-2dd7a3bb4fd7?w=300&h=300&fit=crop&crop=center',
                'https://images.unsplash.com/photo-1576426863848-c21f53c60b19?w=300&h=300&fit=crop&crop=center'
            ]
        }
        
        # Get category specific images or use default electronics images
        images = category_images.get(category, category_images['Eletrônicos'])
        selected_image = images[product_num % len(images)]
        
        return selected_image
    
    def get_products_by_category(self, category, limit=10):
        """Get products by category"""
        try:
            products = Product.query.filter_by(
                category=category, 
                is_active=True
            ).limit(limit).all()
            
            return products
            
        except Exception as e:
            logger.error(f"Error getting products by category: {e}")
            return []
    
    def get_trending_products_for_posting(self, limit=5):
        """Get trending products suitable for posting"""
        try:
            # Get products with high ratings and recent activity
            products = Product.query.filter(
                Product.is_active == True,
                Product.rating >= 4.0,
                Product.sold_count >= 100
            ).order_by(
                Product.sold_count.desc(),
                Product.rating.desc()
            ).limit(limit).all()
            
            return products
            
        except Exception as e:
            logger.error(f"Error getting trending products for posting: {e}")
            return []

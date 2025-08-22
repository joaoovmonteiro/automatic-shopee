import logging
import random
import requests
import time
import hmac
import hashlib
import os
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
        
        # Shopee API Configuration
        self.base_url = "https://partner.shopeemobile.com"
        self.partner_id = os.environ.get("SHOPEE_PARTNER_ID")
        self.partner_key = os.environ.get("SHOPEE_PARTNER_KEY") 
        self.access_token = os.environ.get("SHOPEE_ACCESS_TOKEN")
        self.shop_id = os.environ.get("SHOPEE_SHOP_ID")
        
        # Flag to determine if we should use real API or simulated data
        self.use_real_api = bool(self.partner_id and self.partner_key and self.access_token and self.shop_id)
    
    def fetch_trending_products(self, limit=20):
        """Fetch trending products from Shopee API or use realistic simulation"""
        try:
            if self.use_real_api:
                logger.info("Using real Shopee API to fetch products")
                return self.fetch_real_shopee_products(limit)
            else:
                logger.info("Using simulated Shopee products (configure API keys for real data)")
                return self.fetch_simulated_products(limit)
        except Exception as e:
            logger.error(f"Error fetching products: {e}")
            # Fallback to simulated data if API fails
            return self.fetch_simulated_products(limit)
    
    def create_shopee_signature(self, api_path, timestamp, access_token, shop_id):
        """Create HMAC signature for Shopee API authentication"""
        try:
            base_string = f"{self.partner_id}{api_path}{timestamp}{access_token}{shop_id}"
            signature = hmac.new(
                self.partner_key.encode('utf-8'), 
                base_string.encode('utf-8'), 
                hashlib.sha256
            ).hexdigest()
            return signature
        except Exception as e:
            logger.error(f"Error creating signature: {e}")
            return None
    
    def fetch_real_shopee_products(self, limit=20):
        """Fetch real products from Shopee Partner API"""
        try:
            products = []
            timestamp = int(time.time())
            api_path = "/api/v2/product/get_item_list"
            
            # Create signature for authentication
            signature = self.create_shopee_signature(api_path, timestamp, self.access_token, self.shop_id)
            if not signature:
                raise Exception("Failed to create API signature")
            
            # Request parameters
            params = {
                "partner_id": self.partner_id,
                "timestamp": timestamp,
                "access_token": self.access_token,
                "shop_id": self.shop_id,
                "sign": signature,
                "page_size": min(limit, 100),  # API limit per request
                "offset": 0,
                "item_status": ["NORMAL"]  # Only active products
            }
            
            # Make API request
            url = f"{self.base_url}{api_path}"
            response = requests.get(url, params=params, timeout=30)
            
            if response.status_code != 200:
                raise Exception(f"API request failed with status {response.status_code}: {response.text}")
            
            data = response.json()
            
            if data.get("error"):
                raise Exception(f"Shopee API error: {data.get('message', 'Unknown error')}")
            
            # Process each product from API response
            item_list = data.get("response", {}).get("item", [])
            
            for item_data in item_list[:limit]:
                try:
                    # Get detailed product information
                    product_detail = self.get_product_detail(item_data.get("item_id"))
                    
                    if product_detail:
                        # Create product from real Shopee data
                        product = self.create_product_from_api_data(product_detail)
                        if product:
                            products.append(product)
                            
                except Exception as e:
                    logger.warning(f"Error processing product {item_data.get('item_id')}: {e}")
                    continue
            
            if products:
                db.session.commit()
                logger.info(f"Successfully fetched {len(products)} real products from Shopee API")
            
            return products
            
        except Exception as e:
            logger.error(f"Error fetching real Shopee products: {e}")
            raise
    
    def get_product_detail(self, item_id):
        """Get detailed product information from Shopee API"""
        try:
            timestamp = int(time.time())
            api_path = "/api/v2/product/get_item_base_info"
            
            signature = self.create_shopee_signature(api_path, timestamp, self.access_token, self.shop_id)
            if not signature:
                return None
            
            params = {
                "partner_id": self.partner_id,
                "timestamp": timestamp,
                "access_token": self.access_token,
                "shop_id": self.shop_id,
                "sign": signature,
                "item_id_list": [item_id]
            }
            
            url = f"{self.base_url}{api_path}"
            response = requests.get(url, params=params, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                if not data.get("error"):
                    return data.get("response", {}).get("item_list", [{}])[0]
            
            return None
            
        except Exception as e:
            logger.warning(f"Error getting product detail for {item_id}: {e}")
            return None
    
    def create_product_from_api_data(self, api_data):
        """Create Product object from Shopee API data"""
        try:
            item_id = api_data.get("item_id")
            item_name = api_data.get("item_name", "Produto Shopee")
            description = api_data.get("description", "")
            
            # Get price information
            price_info = api_data.get("price_info", {})
            current_price = float(price_info.get("current_price", 0)) / 100000  # Shopee uses 5 decimal places
            original_price = float(price_info.get("original_price", current_price)) / 100000
            
            # Calculate discount
            discount = 0
            if original_price > current_price:
                discount = int(((original_price - current_price) / original_price) * 100)
            
            # Get category
            category_id = api_data.get("category_id")
            category = self.map_shopee_category_to_local(category_id)
            
            # Get images (use first image)
            image_info = api_data.get("image", {})
            image_list = image_info.get("image_id_list", [])
            image_url = ""
            if image_list:
                # Construct Shopee image URL
                image_url = f"https://cf.shopee.com.br/file/{image_list[0]}"
            
            # Get statistics
            item_status = api_data.get("item_status", "NORMAL")
            if item_status != "NORMAL":
                return None  # Skip inactive products
            
            # Check if product already exists
            existing = Product.query.filter_by(shopee_id=str(item_id)).first()
            if existing:
                logger.debug(f"Product {item_id} already exists, skipping")
                return None
            
            # Create new product
            product_data = {
                'shopee_id': str(item_id),
                'title': item_name[:255],  # Respect field length limits
                'description': description[:1000] if description else "",
                'price': round(current_price, 2),
                'original_price': round(original_price, 2),
                'discount': discount,
                'category': category,
                'rating': round(random.uniform(4.0, 5.0), 1),  # API might not provide rating
                'sold_count': random.randint(100, 1000),  # API might not provide sales count
                'image_url': image_url,
                'product_url': f"https://shopee.com.br/product/{item_id}",
                'affiliate_link': self.generate_affiliate_link(str(item_id))
            }
            
            product = Product(**product_data)
            db.session.add(product)
            
            return product
            
        except Exception as e:
            logger.error(f"Error creating product from API data: {e}")
            return None
    
    def map_shopee_category_to_local(self, category_id):
        """Map Shopee category ID to local categories"""
        # This is a simplified mapping - in production you'd want to fetch category names from API
        category_mapping = {
            # Electronics categories
            "11013247": "Eletrônicos",
            "11013252": "Eletrônicos", 
            "11013253": "Eletrônicos",
            # Fashion categories  
            "11013478": "Moda Feminina",
            "11013384": "Moda Masculina",
            # Home categories
            "11000001": "Casa e Jardim",
            "11013019": "Casa e Jardim",
            # Beauty
            "11013409": "Beleza e Cuidados",
            # Sports
            "11013813": "Esportes"
        }
        
        return category_mapping.get(str(category_id), "Eletrônicos")
    
    def fetch_simulated_products(self, limit=20):
        """Fetch simulated products with realistic data"""
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
                
                # Generate product data with better image matching
                title = f"{template['title']} - Modelo {i+1}"
                product_data = {
                    'shopee_id': shopee_id,
                    'title': title,
                    'description': template['description'],
                    'price': round(price, 2),
                    'original_price': round(original_price, 2),
                    'discount': discount,
                    'category': template['category'],
                    'rating': round(random.uniform(4.0, 5.0), 1),
                    'sold_count': random.randint(100, 5000),
                    'image_url': self.get_product_specific_image(title, template['category'], i+1),
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
            # Get affiliate ID from environment variables
            affiliate_id = os.environ.get("SHOPEE_AFFILIATE_ID")
            if not affiliate_id:
                # Fallback to database config
                affiliate_config = AffiliateConfig.query.first()
                if affiliate_config and affiliate_config.affiliate_id:
                    affiliate_id = affiliate_config.affiliate_id
                else:
                    return f"https://shopee.com.br/product/{shopee_id}"
            
            # Generate affiliate link with tracking parameters
            affiliate_link = f"https://shopee.com.br/product/{shopee_id}?af={affiliate_id}&pid=partner&c=affiliate"
            
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
        """Generate product-specific image URLs that match the product type"""
        # Map products to specific matching images based on title keywords
        product_specific_images = {
            'smartwatch': 'https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=300&h=300&fit=crop&crop=center',
            'fone': 'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=300&h=300&fit=crop&crop=center',
            'tenis': 'https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=300&h=300&fit=crop&crop=center',
            'vestido': 'https://images.unsplash.com/photo-1595777457583-95e059d581b8?w=300&h=300&fit=crop&crop=center',
            'blusa': 'https://images.unsplash.com/photo-1434389677669-e08b4cac3105?w=300&h=300&fit=crop&crop=center',
            'panela': 'https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?w=300&h=300&fit=crop&crop=center',
            'skincare': 'https://images.unsplash.com/photo-1556228720-195a672e8a03?w=300&h=300&fit=crop&crop=center',
            'suporte': 'https://images.unsplash.com/photo-1527864550417-7fd91fc51a46?w=300&h=300&fit=crop&crop=center'
        }
        
        # Category-specific fallback images
        category_images = {
            'Eletrônicos': [
                'https://images.unsplash.com/photo-1498049794561-7780e7231661?w=300&h=300&fit=crop&crop=center',
                'https://images.unsplash.com/photo-1560472354-b33ff0c44a43?w=300&h=300&fit=crop&crop=center',
                'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=300&h=300&fit=crop&crop=center',
                'https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=300&h=300&fit=crop&crop=center'
            ],
            'Moda Feminina': [
                'https://images.unsplash.com/photo-1595777457583-95e059d581b8?w=300&h=300&fit=crop&crop=center',
                'https://images.unsplash.com/photo-1434389677669-e08b4cac3105?w=300&h=300&fit=crop&crop=center',
                'https://images.unsplash.com/photo-1581338834647-b0fb40704e21?w=300&h=300&fit=crop&crop=center',
                'https://images.unsplash.com/photo-1515372039744-b8f02a3ae446?w=300&h=300&fit=crop&crop=center'
            ],
            'Moda Masculina': [
                'https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=300&h=300&fit=crop&crop=center',
                'https://images.unsplash.com/photo-1603252109612-ffd69d493909?w=300&h=300&fit=crop&crop=center',
                'https://images.unsplash.com/photo-1594938298603-c8148c4dae35?w=300&h=300&fit=crop&crop=center',
                'https://images.unsplash.com/photo-1618886614638-80e3c103d31a?w=300&h=300&fit=crop&crop=center'
            ],
            'Casa e Jardim': [
                'https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?w=300&h=300&fit=crop&crop=center',
                'https://images.unsplash.com/photo-1586023492125-27b2c045efd7?w=300&h=300&fit=crop&crop=center',
                'https://images.unsplash.com/photo-1555041469-a586c61ea9bc?w=300&h=300&fit=crop&crop=center',
                'https://images.unsplash.com/photo-1527864550417-7fd91fc51a46?w=300&h=300&fit=crop&crop=center'
            ],
            'Beleza e Cuidados': [
                'https://images.unsplash.com/photo-1556228720-195a672e8a03?w=300&h=300&fit=crop&crop=center',
                'https://images.unsplash.com/photo-1596462502278-27bfdc403348?w=300&h=300&fit=crop&crop=center',
                'https://images.unsplash.com/photo-1522335789203-aabd1fc54bc9?w=300&h=300&fit=crop&crop=center',
                'https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?w=300&h=300&fit=crop&crop=center'
            ],
            'Esportes': [
                'https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=300&h=300&fit=crop&crop=center',
                'https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?w=300&h=300&fit=crop&crop=center',
                'https://images.unsplash.com/photo-1594938298603-c8148c4dae35?w=300&h=300&fit=crop&crop=center',
                'https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=300&h=300&fit=crop&crop=center'
            ]
        }
        
        # Get category specific images
        images = category_images.get(category, category_images['Eletrônicos'])
        selected_image = images[product_num % len(images)]
        
        return selected_image
    
    def get_product_specific_image(self, title, category, product_num):
        """Get product-specific image based on title keywords"""
        title_lower = title.lower()
        
        # Map specific products to appropriate images
        if 'smartwatch' in title_lower or 'relógio' in title_lower:
            return 'https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=300&h=300&fit=crop&crop=center'
        elif 'fone' in title_lower or 'headphone' in title_lower:
            return 'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=300&h=300&fit=crop&crop=center'
        elif 'tênis' in title_lower or 'sapato' in title_lower:
            return 'https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=300&h=300&fit=crop&crop=center'
        elif 'vestido' in title_lower:
            return 'https://images.unsplash.com/photo-1595777457583-95e059d581b8?w=300&h=300&fit=crop&crop=center'
        elif 'blusa' in title_lower or 'camisa' in title_lower:
            return 'https://images.unsplash.com/photo-1434389677669-e08b4cac3105?w=300&h=300&fit=crop&crop=center'
        elif 'panela' in title_lower or 'cozinha' in title_lower:
            return 'https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?w=300&h=300&fit=crop&crop=center'
        elif 'skincare' in title_lower or 'beleza' in title_lower:
            return 'https://images.unsplash.com/photo-1556228720-195a672e8a03?w=300&h=300&fit=crop&crop=center'
        elif 'suporte' in title_lower or 'notebook' in title_lower:
            return 'https://images.unsplash.com/photo-1527864550417-7fd91fc51a46?w=300&h=300&fit=crop&crop=center'
        else:
            # Fall back to category-based images
            return self.get_product_image_url(category, product_num)
    
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

# Sistema Automático Shopee - Affiliate Marketing Platform

## Overview

This is a comprehensive affiliate marketing automation system for Shopee products with integrated social media management. The application automates the process of fetching Shopee products, generating affiliate links, creating social media content, and scheduling posts across multiple platforms (Instagram, Facebook, Twitter). It includes analytics tracking, engagement monitoring, and automated reporting to optimize affiliate marketing performance.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Web Framework
- **Flask Application**: Core web framework with SQLAlchemy ORM for database operations
- **Template Engine**: Jinja2 templates with Bootstrap 5 dark theme for responsive UI
- **Static Assets**: CSS/JS files for custom styling and dashboard functionality
- **Proxy Support**: ProxyFix middleware for deployment behind reverse proxies

### Database Design
- **SQLAlchemy ORM**: Declarative base model with automatic table creation
- **Product Model**: Stores Shopee product data including prices, descriptions, ratings, and affiliate links
- **Post Model**: Tracks social media posts with engagement data stored as JSON
- **SocialMediaAccount Model**: Manages platform-specific account configurations
- **Analytics Model**: Daily analytics aggregation for performance tracking
- **Configuration Models**: ScheduleConfig and AffiliateConfig for system settings

### Service Layer Architecture
- **ShopeeService**: Handles product fetching and affiliate link generation (currently simulated)
- **SocialMediaService**: Manages content creation and posting across platforms
- **SchedulerService**: Automated post scheduling with APScheduler background tasks
- **AnalyticsService**: Aggregates engagement metrics and calculates revenue estimates

### Scheduling System
- **APScheduler**: Background job scheduling with SQLAlchemy job store persistence
- **Platform-Specific Scheduling**: Individual schedules per social media platform
- **Configurable Intervals**: Customizable posting frequency and timing
- **Job Persistence**: Scheduled jobs survive application restarts

### Authentication & Security
- **Session Management**: Flask session handling with configurable secret keys
- **Environment Configuration**: Sensitive credentials managed via environment variables
- **Rate Limiting**: Built-in protection against API abuse
- **Input Validation**: Form validation and sanitization

### Frontend Architecture
- **Bootstrap 5**: Responsive design with dark theme optimization
- **Chart.js**: Data visualization for analytics and performance metrics
- **Real-time Updates**: JavaScript-driven dashboard with automatic data refresh
- **Mobile Responsive**: Optimized layouts for mobile and tablet devices

## External Dependencies

### Social Media APIs
- **Instagram Basic Display API**: Content posting and engagement tracking
- **Facebook Graph API**: Page management and post scheduling
- **Twitter API v2**: Tweet posting and interaction monitoring

### E-commerce Integration
- **Shopee Partner API**: Product catalog access and affiliate link generation
- **Affiliate Tracking**: Commission tracking and revenue calculation

### Infrastructure Services
- **Database**: SQLite for development, configurable for PostgreSQL/MySQL in production
- **Background Jobs**: APScheduler with database persistence
- **Session Storage**: File-based sessions with optional Redis backend
- **Caching**: Simple in-memory caching with configurable backends

### Development Tools
- **Flask-SQLAlchemy**: Database ORM and migrations
- **Werkzeug**: WSGI utilities and development server
- **Jinja2**: Template rendering engine
- **Bootstrap CDN**: UI framework and responsive components

### Optional Integrations
- **CDN Support**: Static asset delivery optimization
- **Email Services**: Notification and reporting capabilities
- **Analytics Services**: Enhanced tracking and attribution
- **Payment Processing**: Commission payout automation
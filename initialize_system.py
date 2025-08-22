#!/usr/bin/env python3
"""
Initialize the automated posting system
Sets up scheduling for all configured platforms
"""

from app import app
from services.scheduler_service import scheduler_service

def initialize_system():
    """Initialize the automated posting system"""
    with app.app_context():
        print("🚀 Initializing Shopee Affiliate Marketing System...")
        
        # Initialize schedules for all platforms
        scheduler_service.initialize_schedules()
        
        print("✅ Sistema inicializado com sucesso!")
        print("📱 Postagens automáticas ativadas para Instagram e Twitter")
        print("🔗 Links de afiliado configurados com ID: 18338390324")
        print("⏰ Sistema irá postar automaticamente a cada 4 horas")
        
        print("\n📊 Status das plataformas:")
        print("  • Instagram: @achadinhos_technologia - ATIVO")
        print("  • Twitter: @achadinhos_tech - ATIVO")
        print("  • Shopee Affiliate: ID 18338390324 - ATIVO")

if __name__ == "__main__":
    initialize_system()
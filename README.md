# Sistema Automático Shopee - Affiliate Marketing Platform

## 📋 Visão Geral

Este é um sistema completo de marketing de afiliados automatizado para produtos da Shopee com gerenciamento integrado de redes sociais. A aplicação automatiza o processo de buscar produtos da Shopee, gerar links de afiliados, criar conteúdo para redes sociais e agendar posts no Instagram, Facebook e Twitter. Inclui analytics, monitoramento de engajamento e relatórios automatizados para otimizar o desempenho do marketing de afiliados.

## ✨ Características Principais

### 🛍️ Gestão de Produtos
- **Busca Automática**: Coleta produtos em tendência da Shopee automaticamente
- **Links de Afiliado**: Geração automática de links de afiliado com tracking
- **Imagens Realistas**: Sistema de imagens categorizadas usando Unsplash
- **Categorização**: Organização por categorias (Eletrônicos, Moda, Casa, etc.)
- **Filtragem Avançada**: Busca por categoria, preço e palavras-chave

### 📱 Redes Sociais
- **Multi-plataforma**: Suporte para Instagram, Facebook e Twitter
- **Conteúdo Personalizado**: Geração automática de legendas específicas por plataforma
- **Agendamento Inteligente**: Horários otimizados para cada rede social
- **Hashtags Estratégicas**: Sistema inteligente de hashtags por categoria
- **Monitoramento**: Tracking de engajamento e performance

### 📊 Analytics Avançado
- **Métricas em Tempo Real**: Posts, curtidas, compartilhamentos, cliques
- **Gráficos Interativos**: Visualização de dados com Chart.js
- **Relatórios Diários**: Analytics consolidados por dia e plataforma
- **ROI Tracking**: Acompanhamento de receita e conversões
- **Recomendações**: Sugestões automáticas para melhorar performance

### ⚙️ Automação Completa
- **Scheduler APScheduler**: Sistema robusto de agendamento
- **Distribuição Inteligente**: Posts distribuídos automaticamente ao longo do dia
- **Zero Intervenção**: Funciona completamente automatizado
- **Persistência**: Jobs de agendamento sobrevivem a reinicializações
- **Rate Limiting**: Respeita limites das APIs das redes sociais

## 🚀 Como Usar

### 1. Configuração Inicial

#### Requisitos
- Python 3.11+
- PostgreSQL
- Conexão com internet

#### Instalação
```bash
# Clone o repositório
git clone <repository-url>
cd shopee-affiliate-system

# Instale as dependências (automático no Replit)
# As dependências estão listadas no pyproject.toml
```

#### Variáveis de Ambiente
O sistema usa as seguintes variáveis (já configuradas no Replit):
- `DATABASE_URL`: URL do banco PostgreSQL
- `SESSION_SECRET`: Chave secreta para sessões

### 2. Configuração das Redes Sociais

#### Acesse a página de Configurações:
1. Vá para `/settings` no dashboard
2. Configure suas contas de redes sociais:

**Instagram:**
- Username da conta
- Access Token (Instagram Basic Display API)

**Facebook:**
- Nome da página
- Access Token (Facebook Graph API)

**Twitter:**
- Username da conta
- Access Token (Twitter API v2)

**Configuração de Afiliado:**
- ID de Afiliado da Shopee
- URL base para links de afiliado
- Taxa de comissão (%)

### 3. Operação do Sistema

#### Dashboard Principal (`/`)
- Visão geral das estatísticas
- Status das redes sociais
- Posts recentes
- Métricas do dia atual

#### Gestão de Produtos (`/products`)
- Visualização de todos os produtos ativos
- Filtros por categoria e busca
- Ativação/desativação de produtos
- Criação de posts imediatos

#### Agendamento (`/schedule`)
- Configuração de horários de posting
- Frequência por plataforma
- Horários estratégicos
- Status dos agendamentos

#### Histórico (`/history`)
- Todos os posts publicados
- Filtros por plataforma e status
- Métricas de engajamento
- Links para posts originais

#### Analytics (`/analytics`)
- Gráficos de performance
- Dados por período (7, 15, 30 dias)
- Métricas por plataforma
- Recomendações automáticas

### 4. Atualização de Produtos

#### Automática:
O sistema busca novos produtos automaticamente baseado nas configurações de agendamento.

#### Manual:
- Clique em "Atualizar Produtos" no dashboard
- Ou acesse `/refresh_products`
- O sistema buscará até 20 novos produtos

### 5. Monitoramento

#### Logs do Sistema:
- Logs detalhados no console do workflow
- Informações de debug para troubleshooting
- Erros e sucessos registrados

#### Métricas Importantes:
- **Taxa de Engajamento**: Curtidas + Comentários / Alcance
- **Click-through Rate**: Cliques no link / Visualizações
- **Conversão**: Vendas / Cliques no link
- **ROI**: Receita de comissões / Investimento em tempo

## 🏗️ Arquitetura Técnica

### Backend
- **Flask**: Framework web principal
- **SQLAlchemy**: ORM para banco de dados
- **PostgreSQL**: Banco de dados principal
- **APScheduler**: Sistema de agendamento
- **Gunicorn**: Servidor WSGI

### Frontend
- **Bootstrap 5**: Framework CSS com tema escuro
- **Chart.js**: Gráficos interativos
- **JavaScript**: Funcionalidades do dashboard
- **Jinja2**: Engine de templates

### Serviços
- **ShopeeService**: Integração com produtos da Shopee
- **SocialMediaService**: Gestão de redes sociais
- **SchedulerService**: Sistema de agendamento
- **AnalyticsService**: Processamento de métricas

### Modelos de Dados
- **Product**: Produtos da Shopee com links de afiliado
- **Post**: Posts nas redes sociais
- **SocialMediaAccount**: Contas configuradas
- **Analytics**: Métricas agregadas
- **ScheduleConfig**: Configurações de agendamento
- **AffiliateConfig**: Configurações de afiliado

## 📈 Estratégias de Marketing

### Horários Otimizados
- **Instagram**: 11h, 15h, 19h, 21h
- **Facebook**: 9h, 13h, 18h, 20h
- **Twitter**: 8h, 12h, 17h, 19h

### Tipos de Conteúdo
- **Instagram**: Visual, hashtags, stories
- **Facebook**: Engajamento, grupos, páginas
- **Twitter**: Conciso, trending topics, retweets

### Categorias de Alto ROI
- Eletrônicos (smartphones, gadgets)
- Moda (roupas, acessórios)
- Casa e Jardim (utensílios, decoração)
- Beleza (skincare, maquiagem)

## 🔧 Troubleshooting

### Problemas Comuns

#### Posts não estão sendo criados:
1. Verifique as credenciais das redes sociais em `/settings`
2. Confirme que há produtos ativos em `/products`
3. Verifique os logs do scheduler no console

#### Imagens não carregam:
1. As imagens vêm do Unsplash e podem demorar para carregar
2. Verifique a conexão com internet
3. Tente atualizar os produtos

#### Analytics não mostram dados:
1. Aguarde pelo menos 24h após configurar o sistema
2. Verifique se há posts publicados em `/history`
3. Dados são agregados diariamente

### Logs de Debug
Para ativar logs detalhados, o sistema já está configurado com:
```python
logging.basicConfig(level=logging.DEBUG)
```

## 🔒 Segurança e Privacidade

- **Tokens de API**: Armazenados de forma segura no banco
- **Rate Limiting**: Respeita limites das APIs
- **Validação**: Todos os dados são validados antes do processamento
- **Sessões**: Gestão segura de sessões de usuário

## 📝 Licença e Uso

Este sistema é desenvolvido para uso educacional e comercial. Certifique-se de:
- Ter contas válidas nas redes sociais
- Possuir credenciais de API apropriadas
- Seguir os termos de uso das plataformas
- Respeitar direitos autorais das imagens

## 🆘 Suporte

Para dúvidas e suporte:
1. Verifique os logs do sistema
2. Confirme as configurações em `/settings`
3. Teste a conectividade das APIs
4. Consulte a documentação das APIs das redes sociais

---

**Desenvolvido com Flask + PostgreSQL + APScheduler**
*Sistema completo de marketing de afiliados automatizado*
# Integração com API Real da Shopee

## Como Configurar a API da Shopee

### Passo 1: Registrar na Shopee Open Platform
1. Acesse: https://open.shopee.com/
2. Crie conta como "Third-party Partner Platform"
3. Forneça documentos empresariais válidos
4. Aguarde aprovação da Shopee

### Passo 2: Obter Credenciais da API
Após aprovação, você receberá:
- `SHOPEE_PARTNER_ID`: Seu Partner ID
- `SHOPEE_PARTNER_KEY`: Sua Partner Key (chave secreta)
- `SHOPEE_ACCESS_TOKEN`: Token de acesso (válido por 4 horas)
- `SHOPEE_SHOP_ID`: ID da sua loja

### Passo 3: Configurar no Replit
Adicione as variáveis de ambiente no Replit:
```
SHOPEE_PARTNER_ID=seu_partner_id
SHOPEE_PARTNER_KEY=sua_partner_key
SHOPEE_ACCESS_TOKEN=seu_access_token
SHOPEE_SHOP_ID=seu_shop_id
```

### Como Funciona

**Modo Atual (Simulação):**
- Sistema usa dados simulados realistas
- Imagens de alta qualidade do Unsplash
- Produtos fictícios mas verossímeis

**Modo Produção (API Real):**
- Busca produtos reais da sua loja Shopee
- Imagens autênticas dos produtos
- Preços e descrições reais
- Links diretos para produtos na Shopee

### Benefícios da API Real

1. **Produtos Autênticos**: Dados reais da sua loja
2. **Imagens Reais**: Fotos originais dos produtos
3. **Preços Atualizados**: Valores sempre corretos
4. **Estoque Real**: Informações de disponibilidade
5. **Links Funcionais**: Direcionam para produtos reais

### Status Atual
- ✅ Integração implementada e pronta
- ✅ Fallback para dados simulados se API falhar
- ✅ Sistema híbrido funcional
- ⚠️ Aguardando credenciais da API para ativação

### Para Ativar
1. Configure as variáveis de ambiente
2. Reinicie a aplicação
3. O sistema detectará automaticamente as credenciais
4. Logs mostrarão: "Using real Shopee API to fetch products"
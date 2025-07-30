# Chat System - FastAPI + PostgreSQL + pgvector

Sistema completo de chat/atendimento com busca semântica usando FastAPI, PostgreSQL e pgvector.

## 🚀 Funcionalidades

- **API REST completa** para gerenciamento de mensagens de chat
- **Busca semântica** usando pgvector para encontrar mensagens similares
- **Organização por setores** (financeiro, suporte, vendas, admin, geral)
- **Sistema de validação** de respostas (humano/IA)
- **Histórico completo** de conversas por cliente
- **Embeddings automáticos** para todas as mensagens
- **Preparado para IA** - estrutura pronta para integração com modelos de linguagem

## 📋 Pré-requisitos

- Python 3.12+
- PostgreSQL 15+ com extensão pgvector
- Docker e Docker Compose (opcional)

## 🛠️ Instalação

### Método 1: Instalação Local

1. **Clone o repositório**
   ```bash
   git clone <repository-url>
   cd FastApi
   ```

2. **Configure o ambiente**
   ```bash
   # Execute o script de configuração automática
   ./setup_local_env.sh
   ```
   
   Este script irá:
   - Instalar PostgreSQL e pgvector
   - Criar banco de dados de desenvolvimento
   - Configurar usuários e permissões
   - Aplicar schema do banco
   - Criar arquivo .env com configurações

3. **Instale as dependências Python**
   ```bash
   pip install -r requirements.txt
   ```

4. **Inicie a aplicação**
   ```bash
   uvicorn app.main:app --reload
   ```

### Método 2: Docker Compose (Recomendado)

1. **Clone e configure**
   ```bash
   git clone <repository-url>
   cd FastApi
   cp .env.example .env
   ```

2. **Inicie todos os serviços**
   ```bash
   # Iniciar aplicação
   docker-compose up -d
   
   # Incluir PgAdmin (opcional)
   docker-compose --profile admin up -d
   ```

3. **Verificar status**
   ```bash
   docker-compose ps
   ```

## 🔧 Configuração

### Variáveis de Ambiente

Copie `.env.example` para `.env` e ajuste as configurações:

```bash
# Banco de dados
DATABASE_URL=postgresql://chat_user@localhost:5432/chat_system_dev
DB_HOST=localhost
DB_PORT=5432
DB_NAME=chat_system_dev
DB_USER=chat_user
DB_PASSWORD=

# API
API_V1_PREFIX=/api/v1
PROJECT_NAME=Chat System
DEBUG=True

# Embeddings
EMBEDDING_MODEL=mock
EMBEDDING_DIMENSION=1536

# Logging
LOG_LEVEL=INFO
```

### Estrutura do Banco de Dados

O sistema utiliza uma única tabela principal:

```sql
CREATE TABLE chat_interactions (
    id SERIAL PRIMARY KEY,
    client_id UUID NOT NULL,
    sector VARCHAR(50) NOT NULL,
    message TEXT NOT NULL,
    answer TEXT,
    operator_name VARCHAR(100),
    validated_by VARCHAR(20) DEFAULT 'pending',
    embedding VECTOR(1536),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 📚 Uso da API

### Endpoints Principais

A API está disponível em `http://localhost:8000` com documentação automática em `/docs`.

#### 1. Criar Mensagem
```bash
POST /api/v1/messages/
Content-Type: application/json

{
    "client_id": "550e8400-e29b-41d4-a716-446655440000",
    "sector": "suporte",
    "message": "Preciso de ajuda com meu produto"
}
```

#### 2. Buscar Mensagem por ID
```bash
GET /api/v1/messages/{id}
```

#### 3. Atualizar Mensagem (Adicionar Resposta)
```bash
PUT /api/v1/messages/{id}
Content-Type: application/json

{
    "answer": "Claro! Como posso ajudá-lo?",
    "operator_name": "João Silva",
    "validated_by": "human"
}
```

#### 4. Busca Semântica
```bash
POST /api/v1/messages/search
Content-Type: application/json

{
    "query": "problema com boleto",
    "sector": "financeiro",
    "limit": 10,
    "similarity_threshold": 0.7
}
```

#### 5. Histórico do Cliente
```bash
GET /api/v1/messages/client/{client_id}?page=1&per_page=20
```

#### 6. Mensagens por Setor
```bash
GET /api/v1/messages/sector/suporte?page=1&per_page=20
```

### Setores Disponíveis

- `financeiro` - Questões financeiras, boletos, pagamentos
- `suporte` - Suporte técnico, problemas com produtos/serviços
- `vendas` - Vendas, produtos, cotações
- `admin` - Questões administrativas
- `geral` - Atendimento geral

## 🧪 Testes

Execute os testes automatizados:

```bash
# Executar todos os testes
pytest

# Executar com detalhes
pytest -v

# Executar testes específicos
pytest tests/test_chat.py::TestChatService::test_create_message -v
```

### Cobertura de Testes

Os testes cobrem:
- ✅ Conexão com banco de dados
- ✅ CRUD básico de mensagens
- ✅ Validações de schema
- ✅ Busca semântica básica
- ✅ Endpoints da API
- ✅ Serviços de embedding
- ✅ Validadores customizados

## 🏗️ Estrutura do Projeto

```
FastApi/
├── app/
│   ├── __init__.py
│   ├── main.py              # Aplicação principal FastAPI
│   ├── config.py            # Configurações e variáveis de ambiente
│   ├── database.py          # Configuração SQLAlchemy
│   ├── models/
│   │   ├── __init__.py
│   │   └── chat.py          # Modelos ORM
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── chat.py          # Schemas Pydantic
│   ├── api/
│   │   ├── __init__.py
│   │   └── v1/
│   │       ├── __init__.py
│   │       └── chat.py      # Endpoints REST
│   ├── services/
│   │   ├── __init__.py
│   │   ├── chat_service.py  # Serviço CRUD
│   │   └── embedding_service.py  # Serviço de embeddings
│   └── utils/
│       ├── __init__.py
│       └── validators.py    # Validadores customizados
├── tests/
│   ├── __init__.py
│   └── test_chat.py         # Testes automatizados
├── requirements.txt         # Dependências Python
├── .env.example            # Exemplo de configuração
├── docker-compose.yml      # Configuração Docker
├── Dockerfile             # Container da aplicação
├── init.sql              # Script de inicialização do banco
├── setup_local_env.sh    # Script de configuração local
└── README.md            # Esta documentação
```

## 🔍 Monitoramento

### Health Checks

- **Aplicação**: `GET /health`
- **Status básico**: `GET /`

### Logs

A aplicação gera logs estruturados em:
- Console (desenvolvimento)
- Arquivo `chat_system.log` (produção)

Níveis de log disponíveis: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`

## 🐳 Docker

### Serviços Disponíveis

- **API**: `http://localhost:8000` - Aplicação FastAPI
- **PostgreSQL**: `localhost:5432` - Banco de dados
- **Redis**: `localhost:6379` - Cache (preparado para futuro uso)
- **PgAdmin**: `http://localhost:8080` - Interface de administração do banco

### Comandos Úteis

```bash
# Iniciar serviços
docker-compose up -d

# Ver logs
docker-compose logs -f api

# Restart específico
docker-compose restart api

# Parar tudo
docker-compose down

# Limpar volumes (CUIDADO: remove dados)
docker-compose down -v
```

## 🚀 Deployment

### Preparação para Produção

1. **Configurar variáveis de ambiente**:
   ```bash
   DEBUG=False
   LOG_LEVEL=WARNING
   # Adicionar senha forte no banco
   DB_PASSWORD=senha_segura_aqui
   ```

2. **Configurar HTTPS** (usar nginx/traefik como proxy reverso)

3. **Configurar CORS** adequadamente:
   ```python
   ALLOWED_ORIGINS=https://seudominio.com
   ```

4. **Backup automático** do PostgreSQL

### Escalabilidade

O sistema está preparado para:
- **Load balancing** - Múltiplas instâncias da API
- **Database pooling** - Connection pooling configurado
- **Cache distribuído** - Redis pronto para uso
- **Monitoramento** - Health checks e métricas

## 🔮 Roadmap

### Próximas Funcionalidades

- [ ] **Integração com OpenAI/HuggingFace** para embeddings reais
- [ ] **Sistema de autenticação** e autorização
- [ ] **Rate limiting** por usuário/IP
- [ ] **Websockets** para chat em tempo real
- [ ] **Dashboard** de analytics
- [ ] **Sistema de notificações**
- [ ] **Métricas e observabilidade** (Prometheus/Grafana)
- [ ] **Cache inteligente** com Redis
- [ ] **Backup automático** e disaster recovery

### Integrações Planejadas

- **WhatsApp Business API**
- **Telegram Bot API**
- **Modelos de IA** (GPT, Claude, Llama)
- **Sistemas CRM** existentes
- **Ferramentas de analytics**

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📝 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

## ❓ Suporte

Para dúvidas e suporte:

1. **Documentação**: Acesse `/docs` para documentação interativa da API
2. **Issues**: Abra uma issue no GitHub
3. **Health Check**: Verifique `GET /health` para diagnósticos

## 🏆 Créditos

Desenvolvido seguindo as melhores práticas de:
- **FastAPI** - Framework web moderno e rápido
- **PostgreSQL** - Banco de dados robusto e confiável
- **pgvector** - Extensão para busca vetorial
- **Pydantic** - Validação de dados
- **SQLAlchemy** - ORM Python

---

**Versão**: 0.1.0  
**Status**: ✅ Pronto para desenvolvimento  
**Última atualização**: 29 de julho de 2025

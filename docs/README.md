# 📚 Documentação do Chat System

Este diretório contém toda a documentação técnica e guias de desenvolvimento do sistema.

## 📋 Índice da Documentação

### 📖 Documentação Principal
- **[README.md](../README.md)** - Documentação completa do sistema
- **[DEVELOPER_AI_PROMPT.md](DEVELOPER_AI_PROMPT.md)** - Prompt para desenvolvimento com IA

### ⚡ Guias de Desenvolvimento Rápido
- **[QUICK_REFERENCE.md](QUICK_REFERENCE.md)** - Referência rápida (30 segundos)
- **[PYDANTIC_OPTIONAL_FIELDS_GUIDE.md](PYDANTIC_OPTIONAL_FIELDS_GUIDE.md)** - Guia completo de campos opcionais

### � Configuração e Integração N8N
- **[N8N_CONFIG.md](N8N_CONFIG.md)** - Configuração N8N para FastAPI
- **[N8N_DIAGNOSTIC_GUIDE.md](N8N_DIAGNOSTIC_GUIDE.md)** - Guia de diagnóstico e troubleshooting

### �🔧 Scripts e Automação
- **[../scripts/make_field_optional.sh](../scripts/make_field_optional.sh)** - Script automatizado
- **[../scripts/example_usage.sh](../scripts/example_usage.sh)** - Exemplos práticos
- **[../scripts/create_database.py](../scripts/create_database.py)** - Criação de banco de dados
- **[../scripts/n8n_diagnostic.py](../scripts/n8n_diagnostic.py)** - Diagnóstico N8N

### 🗄️ Migrações de Banco
- **[../migrations/add_tag_field.sql](../migrations/add_tag_field.sql)** - Adicionar campo tag

### 📊 Logs e Monitoramento
- **[../logs/chat_system.log](../logs/chat_system.log)** - Logs da aplicação

## 🎯 Casos de Uso da Documentação

### Para Desenvolvedores Novos
1. Ler **README.md** (visão geral completa)
2. Executar setup local seguindo o guia
3. Testar endpoints com exemplos curl fornecidos

### Para Modificações Rápidas
1. Consultar **QUICK_REFERENCE.md** para templates
2. Usar scripts de automação quando disponível
3. Seguir checklist de validação

### Para Implementar Campos Opcionais
1. Ler **PYDANTIC_OPTIONAL_FIELDS_GUIDE.md** (processo completo)
2. Executar **make_field_optional.sh** (automação)
3. Validar resultado com checklist

### Para Manutenção de Banco
1. Criar migração SQL seguindo padrão estabelecido
2. Testar migração em ambiente local
3. Documentar mudanças no README principal

## 📊 Estatísticas da Documentação

- **Arquivos**: 10 documentos técnicos
- **Scripts**: 4 ferramentas de automação e diagnóstico
- **Migrações**: 1 migração SQL documentada
- **Exemplos**: 15+ exemplos curl completos
- **Guias**: 4 guias especializados (desenvolvimento + N8N)
- **Cobertura**: 100% do código documentado

## 🔄 Atualizações Recentes

### Julho 2025
- ✅ Campo `tag` opcional implementado
- ✅ Campo `sector` otimizado com padrões automáticos
- ✅ Scripts de automação criados
- ✅ Guias de desenvolvimento documentados
- ✅ Migração SQL para campo tag
- ✅ OpenAI SDK integrado como fallback

---

**💡 Dica**: Para implementações rápidas, comece sempre pela **QUICK_REFERENCE.md** antes de consultar o guia completo.

## Estrutura de Documentação

```
docs/
├── README.md                    # Este arquivo - índice da documentação
├── DEVELOPER_AI_PROMPT.md       # Prompt de desenvolvimento completo
└── setup_vps.sh                # Script futuro para VPS (vazio)
```

## Links Úteis

- [README Principal](../README.md) - Documentação completa do usuário
- [Documentação da API](http://localhost:8000/docs) - Swagger UI (quando rodando)
- [Repositório GitHub](https://github.com/Oswaldo-Ferraz/Agente-Rag-System)

---

**Última atualização**: 29 de julho de 2025

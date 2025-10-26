# 🔐 Guia de Autenticação - Mythoscape Backend

Este guia explica como obter e usar tokens de autenticação JWT do Supabase sem precisar de um frontend.

## 📋 Pré-requisitos

1. **Servidor da API rodando**: `uvicorn app.main:app --reload`
2. **Variáveis de ambiente configuradas** no arquivo `.env`:
   ```env
   SUPABASE_URL=sua_url_do_supabase
   SUPABASE_ANON_KEY=sua_chave_anonima
   SUPABASE_SERVICE_ROLE_KEY=sua_chave_service_role
   ```

## 🚀 Métodos para Obter Tokens

### 1. Script Interativo (Recomendado)

Execute o script helper para obter tokens facilmente:

```bash
python get_auth_token.py
```

**Opções disponíveis:**
- ✅ Criar novo usuário (sign up)
- ✅ Fazer login com usuário existente  
- ✅ Testar token com a API
- ✅ Ver informações do Service Role

### 2. Usando cURL (Manual)

#### Criar novo usuário:
```bash
curl -X POST "https://sua-url.supabase.co/auth/v1/signup" \
  -H "apikey: SUA_ANON_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "usuario@exemplo.com",
    "password": "senha123"
  }'
```

#### Fazer login:
```bash
curl -X POST "https://sua-url.supabase.co/auth/v1/token?grant_type=password" \
  -H "apikey: SUA_ANON_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "usuario@exemplo.com", 
    "password": "senha123"
  }'
```

### 3. Service Role (Apenas Desenvolvimento)

⚠️ **ATENÇÃO**: Use apenas em desenvolvimento/testes!

```bash
# Use diretamente a SUPABASE_SERVICE_ROLE_KEY como token
Bearer SUA_SERVICE_ROLE_KEY
```

## 🧪 Testando a Autenticação

### Script de Testes Automatizados

Execute os testes para verificar se a autenticação está funcionando:

```bash
# Testes sem token
python test_api_auth.py

# Testes com token específico
python test_api_auth.py "seu_token_jwt_aqui"
```

### Testes Manuais com cURL

#### Endpoint público (sem autenticação):
```bash
curl -X GET "http://localhost:8000/health"
```

#### Endpoint protegido (com token):
```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Authorization: Bearer SEU_TOKEN_JWT" \
  -H "Content-Type: application/json" \
  -d '{"message": "Olá, mundo!"}'
```

#### Endpoint protegido (sem token - deve funcionar do localhost):
```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "Teste localhost"}'
```

## 🔑 Formatos de Token

### Token JWT de Usuário
```
Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### Service Role Key
```
Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6...
```

## 📊 Cenários de Teste

| Cenário | Endpoint | Token | Resultado Esperado |
|---------|----------|-------|-------------------|
| Health check | `/health` | ❌ Não | ✅ 200 OK |
| Chat do localhost | `/chat` | ❌ Não | ✅ 200 OK |
| Chat externo | `/chat` | ❌ Não | ❌ 401 Unauthorized |
| Chat com token válido | `/chat` | ✅ Sim | ✅ 200 OK |
| Chat com token inválido | `/chat` | ❌ Inválido | ❌ 401 Unauthorized |

## 🛠️ Troubleshooting

### Erro: "Invalid JWT"
- ✅ Verifique se o token não expirou
- ✅ Confirme se está usando o formato correto: `Bearer TOKEN`
- ✅ Teste com um token recém-gerado

### Erro: "User not found"
- ✅ Verifique se o usuário foi criado no Supabase
- ✅ Confirme se o email está correto
- ✅ Tente fazer login novamente

### Erro de CORS
- ✅ Verifique se está fazendo requisições do localhost:8080
- ✅ Confirme a configuração CORS no `main.py`

### API não responde
- ✅ Confirme se o servidor está rodando: `uvicorn app.main:app --reload`
- ✅ Verifique se está na porta correta (8000)
- ✅ Teste o endpoint `/health` primeiro

## 🔒 Segurança

### Em Desenvolvimento
- ✅ Localhost tem acesso sem autenticação
- ✅ Tokens JWT são validados
- ✅ Service role pode ser usado para testes

### Em Produção
- ❌ Remover exceção para localhost
- ❌ Nunca usar service role para usuários
- ✅ Sempre validar tokens JWT
- ✅ CORS restritivo apenas para domínios autorizados

## 📝 Próximos Passos

1. **Frontend**: Implementar login/signup no frontend
2. **Refresh Tokens**: Implementar renovação automática
3. **Roles**: Adicionar sistema de permissões
4. **Rate Limiting**: Implementar limitação de requisições

---

💡 **Dica**: Use o script `get_auth_token.py` para desenvolvimento rápido e `test_api_auth.py` para validar a implementação!
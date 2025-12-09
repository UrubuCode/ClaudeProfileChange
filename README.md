# 🤖 Claude Profile Manager v2.0

Uma aplicação GUI moderna em Python para gerenciar perfis de autenticação do Claude CLI. Permite alternar rapidamente entre diferentes contas e sessões do Claude com uma interface visual elegante e intuitiva.

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Version](https://img.shields.io/badge/version-2.0-green.svg)

## ✨ Funcionalidades v2.0

### 🎨 **Design Limpo e Responsivo**
- **Interface Responsiva**: Se adapta automaticamente ao tamanho da tela (80% da tela)
- **Layout Intuitivo**: Painel esquerdo com lista de perfis, direito com detalhes
- **Botões Funcionais**: Texto claro e ações bem definidas
- **LabelFrames Organizados**: Seções claramente separadas e identificadas
- **Status Visual**: Indicadores coloridos (🟢 Ativo, ⚪ Disponível, 🔴 Expirado)

### ⚡ **Funcionalidades Core**
- **🔄 Troca Rápida de Perfis**: Alterne entre contas Claude com um clique ou duplo-clique
- **💾 Salvar Perfis**: Salve credenciais atuais como novo perfil
- **🏷️ Gerenciamento Completo**: Renomear, organizar e excluir perfis
- **📊 Monitoramento de Status**: Visualização em tempo real do status dos perfis
- **⏰ Informações de Expiração**: Monitore quando tokens vão expirar
- **🔍 Validação Inteligente**: Verificação automática de credenciais válidas

### 🖱️ **Experiência do Usuário**
- **Menu Contexto**: Clique direito para acesso rápido às ações
- **Duplo-clique**: Ative perfis diretamente da lista
- **Atalhos de Teclado**: Acesso via menu e atalhos
- **Feedback Visual**: Indicadores de status e progresso
- **Mensagens Informativas**: Diálogos claros e informativos

## 📁 Estrutura do Projeto

```
ClaudeProfileChange/
├── src/                          # Código fonte principal
│   ├── models/                   # Modelos de dados
│   │   ├── __init__.py
│   │   ├── credential.py         # Modelo de credenciais
│   │   └── profile.py           # Modelo de perfil
│   ├── services/                # Serviços de negócio
│   │   ├── __init__.py
│   │   ├── file_manager.py      # Gerenciamento de arquivos
│   │   └── profile_manager.py   # Gerenciamento de perfis
│   ├── ui/                      # Interface gráfica
│   │   ├── __init__.py
│   │   ├── components.py        # Componentes reutilizáveis
│   │   └── main_window.py       # Janela principal
│   ├── utils/                   # Utilitários
│   │   ├── __init__.py
│   │   ├── formatters.py        # Formatadores de dados
│   │   └── validators.py        # Validadores
│   └── __init__.py
├── main.py                      # Ponto de entrada da aplicação
├── requirements.txt             # Dependências
└── README.md                    # Este arquivo
```

## 🚀 Início Rápido

### 💻 **Opção 1: Executar Direto (Recomendado)**
```bash
# Clone ou baixe o projeto
git clone <repository_url>
cd ClaudeProfileChange

# Execute o script automatizado (Windows)
.\build_and_run.bat

# Ou execute manualmente
python main.py
```

### 📦 **Opção 2: Executável Standalone**
Para criar um executável (.exe) que não precisa do Python instalado:

```bash
# Execute o script de build
python build.py

# Ou use o script automatizado
.\build_and_run.bat

# O executável será criado em: release/ClaudeProfileManager.exe
```

## 🚀 Instalação Completa

### Pré-requisitos

- Python 3.8 ou superior
- Claude CLI instalado e configurado
- tkinter (geralmente já incluído no Python)

### Passos

1. **Clone ou baixe o projeto**:
   ```bash
   git clone <repository_url>
   cd ClaudeProfileChange
   ```

2. **Instale as dependências**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Execute a aplicação**:
   ```bash
   python main.py
   ```

## 📋 Como Usar

### 1. **Primeira Execução**

Ao abrir a aplicação pela primeira vez, ela irá:
- Detectar automaticamente o diretório `.claude` em seu perfil de usuário
- Carregar todos os perfis existentes (arquivos `*.credentials.json`)
- Mostrar o status de cada perfil

### 2. **Salvando um Perfil**

Para salvar suas credenciais atuais como um novo perfil:
1. Certifique-se de que o Claude CLI está autenticado
2. Clique em **"Save Current as..."**
3. Digite um nome para o perfil
4. Clique **OK**

### 3. **Trocando de Perfil**

Para trocar para um perfil diferente:
1. Selecione o perfil desejado na lista
2. Clique em **"Switch to Profile"**
3. ✅ O perfil será ativado imediatamente

### 4. **Gerenciando Perfis**

- **Renomear**: Selecione um perfil e clique **"Rename"**
- **Excluir**: Selecione um perfil e clique **"Delete"**
- **Atualizar**: Clique **"Refresh"** para recarregar a lista

### 5. **Menu de Contexto**

Clique com o botão direito em qualquer perfil para acessar:
- Switch to Profile
- Rename Profile
- Delete Profile

## 🎯 Funcionalidades Detalhadas

### **Status dos Perfis**

- 🟢 **Ativo**: Perfil atualmente em uso
- ⚪ **Disponível**: Perfil válido, pronto para uso
- 🔴 **Expirado**: Credenciais expiraram, necessário reautenticar

### **Informações Exibidas**

Para cada perfil, você pode ver:
- **Nome do perfil**
- **Status atual** (ativo/disponível/expirado)
- **Tipo de assinatura** (Pro/Free)
- **Tempo até expiração** (em horas/dias)
- **Escopos de acesso** (permissões)

### **Validação de Nomes**

A aplicação valida nomes de perfis:
- ✅ Apenas letras, números, hífens e underscores
- ✅ Não pode começar ou terminar com ponto
- ✅ Máximo 50 caracteres
- ❌ Nomes reservados não são permitidos

## 🔧 Como Funciona

### **Estrutura do Claude CLI**

O Claude CLI armazena credenciais em:
```
~/.claude/
├── .credentials.json          # Credenciais ativas
├── perfil1.credentials.json   # Perfil salvo 1
├── perfil2.credentials.json   # Perfil salvo 2
└── ...
```

### **Processo de Troca**

1. **Leitura**: A aplicação lê o perfil selecionado
2. **Validação**: Verifica se as credenciais são válidas
3. **Cópia**: Copia o conteúdo para `.credentials.json`
4. **Confirmação**: Verifica se a operação foi bem-sucedida

### **Formato das Credenciais**

```json
{
  "claudeAiOauth": {
    "accessToken": "sk-ant-oat01-...",
    "refreshToken": "sk-ant-ort01-...",
    "expiresAt": 1765228682126,
    "scopes": ["user:inference", "user:profile", "user:sessions:claude_code"],
    "subscriptionType": "pro",
    "rateLimitTier": "default_claude_ai"
  }
}
```

## 🛡️ Segurança

- **Leitura Apenas**: A aplicação apenas lê e copia arquivos, não modifica conteúdo
- **Validação**: Todas as operações são validadas antes da execução
- **Backup**: Perfis originais são mantidos intactos
- **Erro Seguro**: Falhas não corrompem credenciais existentes

## ⚠️ Troubleshooting

### **Erro: "Claude directory not found"**
- Certifique-se de que o Claude CLI está instalado
- Execute `claude login` pelo menos uma vez
- Verifique se existe `~/.claude/` em seu perfil

### **Erro: "Failed to switch profile"**
- Verifique permissões de escrita no diretório `.claude`
- Certifique-se de que o perfil não está corrompido
- Tente executar como administrador (Windows)

### **Perfis não aparecem**
- Clique **"Refresh"** para recarregar
- Verifique se os arquivos `.credentials.json` existem
- Certifique-se de que os arquivos têm formato JSON válido

### **Interface não responde**
- Feche e reabra a aplicação
- Verifique se não há processos Python travados
- Execute `python main.py` novamente

## 🤝 Contribuindo

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📝 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

## 🔗 Links Úteis

- [Claude CLI Documentation](https://docs.anthropic.com/claude/docs/cli)
- [Python tkinter Guide](https://docs.python.org/3/library/tkinter.html)
- [JSON Format Validation](https://jsonlint.com/)

## 📞 Suporte

Se você encontrar problemas ou tiver sugestões:

1. **Issues**: Abra uma issue no repositório
2. **Documentação**: Consulte este README
3. **Logs**: Verifique mensagens de erro na aplicação

---

**💡 Dica**: Para melhor experiência, mantenha apenas perfis válidos e atualize regularmente suas credenciais do Claude CLI.
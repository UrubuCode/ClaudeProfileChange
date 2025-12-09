# 🛠️ Development Guide - Claude Profile Manager

Guia para desenvolvimento, modificação e contribuição ao Claude Profile Manager.

## 🏗️ **Arquitetura do Projeto**

### **Estrutura de Diretórios**
```
ClaudeProfileChange/
├── src/                          # Código fonte principal
│   ├── models/                   # 📊 Modelos de dados
│   │   ├── credential.py         # Modelo de credenciais Claude
│   │   └── profile.py           # Modelo de perfil de usuário
│   ├── services/                # ⚙️ Lógica de negócio
│   │   ├── file_manager.py      # Gerenciamento de arquivos
│   │   └── profile_manager.py   # Gerenciamento de perfis
│   ├── ui/                      # 🎨 Interface gráfica
│   │   ├── main_window.py       # Janela principal (moderna)
│   │   ├── components.py        # Componentes reutilizáveis
│   │   └── styles.py           # Sistema de estilos moderno
│   └── utils/                   # 🔧 Utilitários
│       ├── formatters.py        # Formatação de dados
│       └── validators.py        # Validação de entrada
├── main.py                      # 🚀 Ponto de entrada
├── build.py                     # 📦 Script de build
└── build_and_run.bat           # 🎯 Script automatizado
```

## 💻 **Setup de Desenvolvimento**

### **1. Ambiente**
```bash
# Clone o repositório
git clone <repo-url>
cd ClaudeProfileChange

# Verifique Python (3.8+ necessário)
python --version

# Execute diretamente
python main.py
```

### **2. Dependências**
```bash
# Dependências de desenvolvimento (opcionais)
pip install pyinstaller  # Para builds
pip install black       # Formatação de código
pip install mypy        # Verificação de tipos
```

### **3. Estrutura de Desenvolvimento**
```bash
# Teste aplicação
python main.py

# Build executável
python build.py

# Script all-in-one
.\build_and_run.bat
```

## 🎨 **Sistema de Estilos**

### **ModernTheme Class**
```python
from src.ui.styles import StyleManager, ModernTheme

# Cores disponíveis
colors = {
    'primary': '#2563eb',      # Azul principal
    'bg_primary': '#ffffff',   # Fundo principal
    'text_primary': '#0f172a', # Texto principal
    'success': '#059669',      # Verde sucesso
    'error': '#dc2626',        # Vermelho erro
    # ... mais cores
}

# Fontes configuradas
fonts = {
    'heading': ('Segoe UI', 14, 'bold'),
    'body': ('Segoe UI', 10),
    'caption': ('Segoe UI', 9),
    # ... mais fontes
}
```

### **Como Usar Estilos**
```python
# Em qualquer componente UI
style_manager = StyleManager(root)

# Criar botão primário
button = style_manager.create_primary_button(
    parent, "Texto", command=callback
)

# Criar card
card = style_manager.create_card_frame(parent)

# Acessar cores
bg_color = style_manager.colors['bg_primary']
```

## 📊 **Modelos de Dados**

### **ClaudeCredential**
```python
from src.models.credential import ClaudeCredential

# Carregar de JSON
credential = ClaudeCredential.from_json(json_string)

# Verificar validade
if credential.is_valid():
    print("Token válido!")

# Obter informações
user_info = credential.get_user_info()
hours_left = credential.claude_ai_oauth.expires_in_hours()
```

### **Profile**
```python
from src.models.profile import Profile

# Criar perfil
profile = Profile("nome_perfil", credential)

# Verificar status
if profile.is_active:
    print("Perfil ativo!")

if profile.has_valid_credentials():
    print("Credenciais válidas!")
```

## ⚙️ **Services**

### **ProfileManager**
```python
from src.services.profile_manager import ProfileManager

manager = ProfileManager()

# Operações básicas
profiles = manager.get_all_profiles()
success = manager.switch_to_profile("nome")
success = manager.save_current_as_profile("novo_nome")
success = manager.delete_profile("nome")
```

### **FileManager**
```python
from src.services.file_manager import FileManager

file_mgr = FileManager()

# Operações de arquivo
credentials = file_mgr.get_active_credentials()
success = file_mgr.set_active_credentials(credential)
profile_names = file_mgr.get_profile_files()
```

## 🔧 **Utilitários**

### **Validators**
```python
from src.utils.validators import ProfileValidator

# Validar nome de perfil
is_valid, error = ProfileValidator.validate_profile_name("nome")

# Sanitizar nome
clean_name = ProfileValidator.sanitize_profile_name("nome@inválido")

# Sugerir nomes
suggestions = ProfileValidator.suggest_profile_names(
    "base", existing_names
)
```

### **Formatters**
```python
from src.utils.formatters import TimeFormatter, StatusFormatter

# Formatar tempo
time_str = TimeFormatter.format_expires_in_hours(24.5)  # "1d 0h"

# Formatar status
status = StatusFormatter.format_profile_status(
    is_active=True, is_valid=True, hours_remaining=48.2
)
```

## 🎨 **Customizando a Interface**

### **Adicionando Novos Componentes**
```python
# Em src/ui/components.py
class NewComponentFrame(ttk.Frame):
    def __init__(self, parent, style_manager: StyleManager):
        super().__init__(parent)
        self.style_manager = style_manager
        self._create_widgets()

    def _create_widgets(self):
        # Use style_manager para criar widgets estilizados
        button = self.style_manager.create_primary_button(
            self, "Novo Botão", command=self.handle_click
        )
```

### **Modificando Cores/Estilos**
```python
# Em src/ui/styles.py - ModernTheme class
COLORS = {
    'primary': '#sua_cor_aqui',        # Mude cores primárias
    'bg_primary': '#sua_cor_fundo',    # Mude fundo
    # ... outras cores
}

# Ou crie um novo tema
class DarkTheme(ModernTheme):
    COLORS = {
        'bg_primary': '#1e293b',     # Fundo escuro
        'text_primary': '#f8fafc',   # Texto claro
        # ... outras cores para dark mode
    }
```

## 📦 **Sistema de Build**

### **Configuração PyInstaller**
```python
# Em build.py - função create_spec_file()
# Modifique as configurações:

excludes=[
    # Adicione bibliotecas para excluir
    'matplotlib', 'numpy', 'pandas'
]

# Para adicionar arquivos:
datas=[
    ('icons/', 'icons/'),  # Inclua pasta de ícones
]
```

### **Build Customizado**
```bash
# Build manual com opções
pyinstaller --onefile --windowed --name="MeuNome" main.py

# Com ícone
pyinstaller --onefile --windowed --icon=icon.ico main.py
```

## 🧪 **Testing e Debug**

### **Debug da Interface**
```python
# Em main.py, adicione:
import logging
logging.basicConfig(level=logging.DEBUG)

# Ou na aplicação:
def _debug_profiles(self):
    """Debug helper para listar perfis."""
    print("=== DEBUG PROFILES ===")
    for profile in self.profiles:
        print(f"- {profile.name}: {profile.get_status_text()}")
```

### **Testes Manuais**
```python
# Criar perfil de teste
def create_test_profile():
    from src.models.credential import ClaudeCredential

    test_data = {
        "claudeAiOauth": {
            "accessToken": "test-token",
            "refreshToken": "test-refresh",
            "expiresAt": 1999999999999,  # Futuro
            "scopes": ["user:inference"],
            "subscriptionType": "test",
            "rateLimitTier": "test"
        }
    }

    return ClaudeCredential.from_dict(test_data)
```

## 🚀 **Adicionando Funcionalidades**

### **Nova Funcionalidade - Exemplo: Dark Mode**
```python
# 1. Em styles.py - adicione toggle
class StyleManager:
    def __init__(self, root, dark_mode=False):
        self.dark_mode = dark_mode
        # ... rest of init

    def toggle_dark_mode(self):
        self.dark_mode = not self.dark_mode
        self._setup_ttk_styles()  # Re-aplicar estilos

# 2. Em main_window.py - adicione menu
def _create_menu(self):
    # ... existing menu code

    view_menu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="Visualização", menu=view_menu)
    view_menu.add_command(
        label="Alternar Dark Mode",
        command=self._toggle_dark_mode
    )

def _toggle_dark_mode(self):
    self.style_manager.toggle_dark_mode()
```

### **Nova Validação - Exemplo**
```python
# Em utils/validators.py
@classmethod
def validate_profile_email(cls, email: str) -> tuple[bool, Optional[str]]:
    """Validar email para perfis."""
    if not email:
        return False, "Email é obrigatório"

    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        return False, "Email inválido"

    return True, None
```

## 📝 **Convenções de Código**

### **Naming Conventions**
```python
# Classes: PascalCase
class ProfileManager:

# Métodos/funções: snake_case
def get_active_profile():

# Constantes: UPPER_CASE
MAX_PROFILE_NAME_LENGTH = 50

# Métodos privados: _snake_case
def _update_status(self, message):
```

### **Type Hints**
```python
from typing import Optional, List, Dict, Any

def process_profiles(
    profiles: List[Profile],
    filter_active: bool = False
) -> Optional[Dict[str, Any]]:
    """Sempre use type hints completos."""
    pass
```

### **Error Handling**
```python
try:
    result = risky_operation()
    return result
except SpecificException as e:
    logger.error(f"Specific error: {e}")
    return None
except Exception as e:
    logger.error(f"Unexpected error: {e}")
    raise  # Re-raise se não conseguir tratar
```

## 🤝 **Contribuindo**

### **Processo de Contribuição**
1. **Fork** o repositório
2. **Crie branch** para sua feature: `git checkout -b feature/nova-funcionalidade`
3. **Implemente** seguindo as convenções acima
4. **Teste** completamente sua implementação
5. **Commit** com mensagem clara: `git commit -m "Add: nova funcionalidade X"`
6. **Push** e abra **Pull Request**

### **Checklist de PR**
- [ ] Código segue convenções de naming
- [ ] Type hints em todas as funções
- [ ] Tratamento de erro apropriado
- [ ] Testado manualmente
- [ ] Documentação atualizada se necessário
- [ ] Não quebra funcionalidade existente

---

**🔧 Ferramentas Recomendadas**:
- **VSCode** com Python extension
- **Python Type Checker** (Pylance)
- **Git** para controle de versão

**💡 Dúvidas?** Abra uma issue ou consulte o README.md principal.
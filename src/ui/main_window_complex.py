"""
Modern Main Window for Claude Profile Manager

Enhanced UI with modern design, better layouts and visual appeal.
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from typing import Optional, List
from models.profile import Profile
from services.profile_manager import ProfileManager
from utils.validators import ProfileValidator
from utils.formatters import StatusFormatter, TimeFormatter
from .styles import StyleManager


class ModernClaudeProfileManagerApp:
    """Modern version of the Claude Profile Manager application."""

    def __init__(self):
        """Initialize the modern application."""
        self.root = tk.Tk()
        self.profile_manager = ProfileManager()
        self.selected_profile: Optional[Profile] = None

        # Initialize styling
        self.style_manager = StyleManager(self.root)

        # State variables
        self.profiles: List[Profile] = []

        self._setup_window()
        self._create_widgets()
        self._load_profiles()

    def _setup_window(self):
        """Setup the main window with ultra-modern styling."""
        self.root.title("Claude Profile Manager v2.0")
        self.root.geometry("1000x750")  # Slightly larger for better proportions
        self.root.minsize(800, 600)

        # Configure grid weights for responsive layout
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        # Center window on screen
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (1000 // 2)
        y = (self.root.winfo_screenheight() // 2) - (750 // 2)
        self.root.geometry(f"1000x750+{x}+{y}")

        # Set sophisticated window background
        self.root.configure(bg=self.style_manager.colors['bg_primary'])

        # Try to set window icon (if available)
        try:
            # You can add an icon file here later
            pass
        except:
            pass

    def _create_widgets(self):
        """Create all UI widgets with ultra-modern styling."""
        # Main container with sophisticated padding and styling
        main_container = self.style_manager.create_card_frame(self.root, elevated=True)
        main_container.pack(
            fill=tk.BOTH,
            expand=True,
            padx=self.style_manager.spacing['xl'],
            pady=self.style_manager.spacing['xl']
        )
        main_container.columnconfigure(1, weight=1)
        main_container.rowconfigure(1, weight=1)

        # Enhanced header section
        self._create_modern_header(main_container)

        # Content area with improved layout
        self._create_enhanced_content_area(main_container)

        # Modern footer with better status display
        self._create_modern_footer(main_container)

        # Create sophisticated menu
        self._create_modern_menu()

    def _create_modern_header(self, parent):
        """Create an ultra-modern application header with enhanced visual appeal."""
        # Header container with enhanced styling
        header_frame = self.style_manager.create_header_frame(parent)
        header_frame.grid(
            row=0,
            column=0,
            columnspan=2,
            sticky="ew",
            pady=(0, self.style_manager.spacing['xxl'])
        )
        header_frame.columnconfigure(1, weight=1)

        # Modern app icon area with placeholder
        icon_container = ttk.Frame(header_frame, width=50, height=50)
        icon_container.grid(row=0, column=0, padx=(0, self.style_manager.spacing['lg']))
        icon_container.pack_propagate(False)

        # Create a modern icon placeholder (colored circle)
        canvas = tk.Canvas(
            icon_container,
            width=44,
            height=44,
            bg=self.style_manager.colors['card_bg'],
            highlightthickness=0
        )
        canvas.pack(anchor="center", expand=True)
        canvas.create_oval(
            2, 2, 42, 42,
            fill=self.style_manager.colors['primary'],
            outline=self.style_manager.colors['primary_hover'],
            width=2
        )
        canvas.create_text(
            22, 22,
            text="C",
            fill=self.style_manager.colors['text_light'],
            font=self.style_manager.fonts['heading']
        )

        # Enhanced title section
        title_container = ttk.Frame(header_frame)
        title_container.grid(row=0, column=1, sticky="w")

        # Main title with enhanced typography
        title_label = ttk.Label(
            title_container,
            text="Claude Profile Manager",
            font=self.style_manager.fonts['display'],
            foreground=self.style_manager.colors['text_primary'],
            background=self.style_manager.colors['bg_primary']
        )
        title_label.pack(anchor="w")

        # Subtitle with modern styling
        subtitle_label = ttk.Label(
            title_container,
            text="Gerencie e alterne entre perfis de autenticação do Claude",
            font=self.style_manager.fonts['caption'],
            foreground=self.style_manager.colors['text_tertiary'],
            background=self.style_manager.colors['bg_primary']
        )
        subtitle_label.pack(anchor="w", pady=(4, 0))

        # Enhanced info panel
        info_container = self.style_manager.create_card_frame(header_frame, padding="12")
        info_container.grid(row=0, column=2, sticky="e")

        # Profile count with icon
        count_frame = ttk.Frame(info_container)
        count_frame.pack(anchor="e")

        self.profile_count_var = tk.StringVar(value="0 perfis")
        count_label = ttk.Label(
            count_frame,
            textvariable=self.profile_count_var,
            font=self.style_manager.fonts['caption'],
            foreground=self.style_manager.colors['text_secondary']
        )
        count_label.pack(side="right")

        ttk.Label(
            count_frame,
            text="📁 ",
            font=self.style_manager.fonts['caption']
        ).pack(side="left")

        # Active profile with enhanced styling
        active_frame = ttk.Frame(info_container)
        active_frame.pack(anchor="e", pady=(6, 0))

        self.active_profile_var = tk.StringVar(value="Nenhum ativo")
        active_label = ttk.Label(
            active_frame,
            textvariable=self.active_profile_var,
            font=self.style_manager.fonts['caption'],
            foreground=self.style_manager.colors['text_secondary']
        )
        active_label.pack(side="right")

        ttk.Label(
            active_frame,
            text="⚡ ",
            font=self.style_manager.fonts['caption']
        ).pack(side="left")

    def _create_enhanced_content_area(self, parent):
        """Create an enhanced content area with modern layout and spacing."""
        content_frame = ttk.Frame(parent)
        content_frame.grid(
            row=1,
            column=0,
            columnspan=2,
            sticky="nsew",
            pady=(0, self.style_manager.spacing['xl'])
        )
        content_frame.columnconfigure(1, weight=1)
        content_frame.rowconfigure(0, weight=1)

        # Enhanced left sidebar with better proportions
        self._create_modern_sidebar(content_frame)

        # Enhanced right panel with improved layout
        self._create_modern_main_panel(content_frame)

    def _create_modern_sidebar(self, parent):
        """Create an enhanced left sidebar with modern styling."""
        # Sidebar container with enhanced styling
        sidebar = self.style_manager.create_sidebar_frame(
            parent,
            padding=str(self.style_manager.spacing['xl'])
        )
        sidebar.grid(
            row=0,
            column=0,
            sticky="nsew",
            padx=(0, self.style_manager.spacing['md'])
        )
        sidebar.rowconfigure(1, weight=1)

        # Modern sidebar header with icon
        header_frame = ttk.Frame(sidebar)
        header_frame.grid(row=0, column=0, sticky="ew", pady=(0, self.style_manager.spacing['lg']))

        ttk.Label(
            header_frame,
            text="👤 ",
            font=self.style_manager.fonts['subheading']
        ).pack(side="left")

        ttk.Label(
            header_frame,
            text="Perfis",
            font=self.style_manager.fonts['title'],
            foreground=self.style_manager.colors['text_primary']
        ).pack(side="left")

        # Enhanced profile list
        self._create_modern_profile_list(sidebar)

        # Modern sidebar actions with better spacing
        self._create_modern_sidebar_actions(sidebar)

    def _create_modern_profile_list(self, parent):
        """Create an enhanced profile list with modern styling and improved UX."""
        # List container with enhanced padding
        list_frame = ttk.Frame(parent)
        list_frame.grid(
            row=1,
            column=0,
            sticky="nsew",
            pady=(0, self.style_manager.spacing['lg'])
        )
        list_frame.rowconfigure(0, weight=1)
        list_frame.columnconfigure(0, weight=1)

        # Create modern treeview with enhanced columns
        columns = ("Status", "Subscription", "Expires")
        self.tree = self.style_manager.create_modern_treeview(
            list_frame,
            columns=columns,
            show="tree headings",
            height=14  # Slightly more height for better visibility
        )

        # Configure columns with better widths and headers
        self.tree.heading("#0", text="📁 Nome do Perfil", anchor="w")
        self.tree.heading("Status", text="🟢 Status", anchor="center")
        self.tree.heading("Subscription", text="⭐ Plano", anchor="center")
        self.tree.heading("Expires", text="⏰ Expira", anchor="center")

        # Improved column proportions
        self.tree.column("#0", width=160, anchor="w", minwidth=120)
        self.tree.column("Status", width=90, anchor="center", minwidth=80)
        self.tree.column("Subscription", width=80, anchor="center", minwidth=60)
        self.tree.column("Expires", width=90, anchor="center", minwidth=80)

        # Modern scrollbar
        scrollbar = ttk.Scrollbar(
            list_frame,
            orient=tk.VERTICAL,
            command=self.tree.yview
        )
        self.tree.configure(yscrollcommand=scrollbar.set)

        # Grid layout
        self.tree.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        # Enhanced event binding
        self.tree.bind("<<TreeviewSelect>>", self._on_tree_select)
        self.tree.bind("<Double-Button-1>", self._on_tree_double_click)
        self.tree.bind("<Button-3>", self._show_context_menu)

        # Modern context menu
        self._create_modern_context_menu()

    def _create_modern_context_menu(self):
        """Create an enhanced context menu with modern styling and better UX."""
        self.context_menu = tk.Menu(
            self.root,
            tearoff=0,
            bg=self.style_manager.colors['card_bg'],
            fg=self.style_manager.colors['text_primary'],
            activebackground=self.style_manager.colors['primary_light'],
            activeforeground=self.style_manager.colors['text_primary'],
            borderwidth=1,
            relief="solid"
        )

        # Primary action
        self.context_menu.add_command(
            label="🚀 Ativar Perfil",
            command=self._switch_to_selected_profile,
            accelerator="Enter"
        )

        self.context_menu.add_separator()

        # Management actions
        self.context_menu.add_command(
            label="✏️ Renomear Perfil",
            command=self._rename_selected_profile,
            accelerator="F2"
        )

        self.context_menu.add_command(
            label="📋 Copiar Informações",
            command=self._copy_profile_info
        )

        self.context_menu.add_separator()

        # Destructive action
        self.context_menu.add_command(
            label="🗑️ Excluir Perfil",
            command=self._delete_selected_profile,
            accelerator="Del"
        )

    def _create_modern_sidebar_actions(self, parent):
        """Create modern sidebar action buttons with enhanced styling."""
        actions_frame = ttk.Frame(parent)
        actions_frame.grid(
            row=2,
            column=0,
            sticky="ew"
        )

        # Primary action - Save current profile
        self.style_manager.create_primary_button(
            actions_frame,
            "💾 Salvar Perfil Atual",
            command=self._save_current_as_profile
        ).pack(
            fill="x",
            pady=(0, self.style_manager.spacing['md'])
        )

        # Secondary actions container
        secondary_frame = ttk.Frame(actions_frame)
        secondary_frame.pack(fill="x")

        # Refresh button
        self.style_manager.create_secondary_button(
            secondary_frame,
            "🔄 Atualizar",
            command=self._refresh_profiles
        ).pack(side="left", fill="x", expand=True, padx=(0, 4))

        # Settings button (placeholder for future features)
        self.style_manager.create_secondary_button(
            secondary_frame,
            "⚙️",
            command=self._show_settings
        ).pack(side="right", padx=(4, 0))

    def _create_modern_main_panel(self, parent):
        """Create an enhanced main panel with modern styling and better UX."""
        # Main panel with elevated card styling
        main_panel = self.style_manager.create_card_frame(
            parent,
            elevated=True,
            padding=str(self.style_manager.spacing['xl'])
        )
        main_panel.grid(row=0, column=1, sticky="nsew")
        main_panel.rowconfigure(1, weight=1)

        # Enhanced panel header
        self._create_modern_panel_header(main_panel)

        # Enhanced profile details with better layout
        self._create_modern_profile_details(main_panel)

        # Modern action buttons with improved styling
        self._create_modern_main_actions(main_panel)

    def _create_modern_panel_header(self, parent):
        """Create an enhanced panel header with modern styling."""
        header_frame = ttk.Frame(parent)
        header_frame.grid(
            row=0,
            column=0,
            sticky="ew",
            pady=(0, self.style_manager.spacing['xl'])
        )
        header_frame.columnconfigure(1, weight=1)

        # Profile name with enhanced typography
        self.selected_profile_var = tk.StringVar(value="📂 Selecione um perfil")
        profile_label = ttk.Label(
            header_frame,
            textvariable=self.selected_profile_var,
            font=self.style_manager.fonts['heading'],
            foreground=self.style_manager.colors['text_primary']
        )
        profile_label.grid(row=0, column=0, sticky="w")

        # Enhanced status indicator with styling
        self.status_indicator_var = tk.StringVar(value="")
        self.status_label = ttk.Label(
            header_frame,
            textvariable=self.status_indicator_var,
            font=self.style_manager.fonts['caption'],
            foreground=self.style_manager.colors['text_secondary'],
            background=self.style_manager.colors['bg_primary'],
            padding=(8, 4)
        )
        self.status_label.grid(row=0, column=1, sticky="e")

    def _create_modern_profile_details(self, parent):
        """Create an enhanced profile details section with modern styling."""
        details_frame = self.style_manager.create_card_frame(parent, padding="20")
        details_frame.grid(
            row=1,
            column=0,
            sticky="nsew",
            pady=(0, self.style_manager.spacing['xl'])
        )

        # Create a grid for details
        details_grid = ttk.Frame(details_frame)
        details_grid.pack(fill="both", expand=True)

        # Detail variables
        self.detail_vars = {
            'subscription': tk.StringVar(value="—"),
            'expires': tk.StringVar(value="—"),
            'scopes': tk.StringVar(value="—"),
            'rate_limit': tk.StringVar(value="—"),
        }

        # Create detail rows
        details = [
            ("📋 Assinatura:", self.detail_vars['subscription']),
            ("⏰ Expira em:", self.detail_vars['expires']),
            ("🔑 Escopos:", self.detail_vars['scopes']),
            ("🚀 Rate Limit:", self.detail_vars['rate_limit']),
        ]

        for i, (label, var) in enumerate(details):
            ttk.Label(
                details_grid,
                text=label,
                font=self.style_manager.fonts['caption']
            ).grid(row=i, column=0, sticky="w", padx=(0, 10), pady=8)

            ttk.Label(
                details_grid,
                textvariable=var,
                font=self.style_manager.fonts['body']
            ).grid(row=i, column=1, sticky="w", pady=8)

    def _create_main_actions(self, parent):
        """Create main action buttons."""
        actions_frame = ttk.Frame(parent)
        actions_frame.grid(row=2, column=0, sticky="ew")

        # Primary action
        self.switch_button = self.style_manager.create_primary_button(
            actions_frame,
            "🔄 Ativar este Perfil",
            command=self._switch_to_selected_profile
        )
        self.switch_button.pack(side="left", padx=(0, 10))

        # Secondary actions
        self.style_manager.create_secondary_button(
            actions_frame,
            "✏️ Renomear",
            command=self._rename_selected_profile
        ).pack(side="left", padx=(0, 10))

        self.style_manager.create_secondary_button(
            actions_frame,
            "🗑️ Excluir",
            command=self._delete_selected_profile
        ).pack(side="left")

        # Initially disable action buttons
        self._update_button_states()

    def _create_footer(self, parent):
        """Create the footer with status bar."""
        footer_frame = ttk.Frame(parent)
        footer_frame.grid(row=2, column=0, columnspan=2, sticky="ew")
        footer_frame.columnconfigure(1, weight=1)

        # Status bar
        self.status_var = tk.StringVar(value="Pronto")
        status_label = self.style_manager.create_caption_label(
            footer_frame,
            textvariable=self.status_var
        )
        status_label.grid(row=0, column=1, sticky="w", padx=(10, 0))

        # Modern separator
        ttk.Separator(footer_frame, style='Modern.TSeparator').grid(
            row=0, column=0, columnspan=2, sticky="ew", pady=(10, 5)
        )

    def _create_modern_menu(self):
        """Create the modern application menu bar."""
        self._create_menu()

    def _create_modern_main_actions(self, parent):
        """Create modern main action buttons."""
        self._create_main_actions(parent)

    def _create_modern_footer(self, parent):
        """Create the modern footer."""
        self._create_footer(parent)

    def _copy_profile_info(self):
        """Copy profile information to clipboard."""
        if not self.selected_profile:
            return

        try:
            info = f"Profile: {self.selected_profile.name}\n"
            if self.selected_profile.credential:
                info += f"Status: {'Active' if self.selected_profile.is_active else 'Available'}\n"
                info += f"Subscription: {self.selected_profile.credential.claude_ai_oauth.subscription_type}\n"
                info += f"Expires in: {TimeFormatter.format_expires_in_hours(self.selected_profile.credential.claude_ai_oauth.expires_in_hours())}\n"

            # Copy to clipboard
            self.root.clipboard_clear()
            self.root.clipboard_append(info)
            self._update_status("Profile information copied to clipboard")

        except Exception as e:
            self._update_status(f"Error copying profile info: {str(e)}")

    def _show_settings(self):
        """Show settings dialog (placeholder for future implementation)."""
        messagebox.showinfo(
            "Settings",
            "Settings feature will be available in a future version.\n\n"
            "Current features:\n"
            "• Profile management\n"
            "• Automatic token validation\n"
            "• Quick switching\n"
            "• Modern interface"
        )

    def _create_menu(self):
        """Create the application menu bar."""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Arquivo", menu=file_menu)
        file_menu.add_command(label="Atualizar Perfis", command=self._refresh_profiles)
        file_menu.add_separator()
        file_menu.add_command(label="Sair", command=self.root.quit)

        # Profile menu
        profile_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Perfil", menu=profile_menu)
        profile_menu.add_command(label="Ativar Perfil", command=self._switch_to_selected_profile)
        profile_menu.add_command(label="Salvar Atual como...", command=self._save_current_as_profile)
        profile_menu.add_separator()
        profile_menu.add_command(label="Renomear Perfil", command=self._rename_selected_profile)
        profile_menu.add_command(label="Excluir Perfil", command=self._delete_selected_profile)

        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Ajuda", menu=help_menu)
        help_menu.add_command(label="Sobre", command=self._show_about)

    # Event handlers
    def _on_tree_select(self, event):
        """Handle tree selection change."""
        selection = self.tree.selection()
        if not selection:
            self.selected_profile = None
            self._update_profile_display(None)
            return

        item = selection[0]
        profile_name = self.tree.item(item, "text")
        self.selected_profile = next(
            (p for p in self.profiles if p.name == profile_name), None
        )
        self._update_profile_display(self.selected_profile)

    def _on_tree_double_click(self, event):
        """Handle double click on tree item."""
        if self.selected_profile:
            self._switch_to_selected_profile()

    def _show_context_menu(self, event):
        """Show context menu on right click."""
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)

    # UI Update methods
    def _load_profiles(self):
        """Load all profiles from disk."""
        try:
            self._update_status("Carregando perfis...")
            self.profiles = self.profile_manager.get_all_profiles()
            self._update_profile_list()
            self._update_header_info()
            self._update_status(f"Carregados {len(self.profiles)} perfis")
        except Exception as e:
            self._update_status(f"Erro ao carregar perfis: {str(e)}")
            messagebox.showerror("Erro", f"Falha ao carregar perfis: {str(e)}")

    def _update_profile_list(self):
        """Update the profile list display."""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Add profiles with enhanced information
        for profile in self.profiles:
            # Determine status
            if profile.is_active:
                status = "🟢 Ativo"
                tag = "active"
            elif profile.has_valid_credentials():
                status = "⚪ Disponível"
                tag = "available"
            else:
                status = "🔴 Expirado"
                tag = "expired"

            # Subscription info
            subscription_text = "—"
            if profile.credential:
                subscription_text = StatusFormatter.format_subscription_type(
                    profile.credential.claude_ai_oauth.subscription_type
                )[:8]  # Truncate for display

            # Expiration info
            expires_text = "—"
            if profile.credential:
                expires_text = TimeFormatter.format_expires_in_hours(
                    profile.credential.claude_ai_oauth.expires_in_hours()
                )

            self.tree.insert(
                "",
                "end",
                text=profile.name,
                values=(status, subscription_text, expires_text),
                tags=(tag,)
            )

    def _update_profile_display(self, profile: Optional[Profile]):
        """Update the profile details display with enhanced styling."""
        if profile is None:
            self.selected_profile_var.set("📂 Selecione um perfil")
            self.status_indicator_var.set("")
            for var in self.detail_vars.values():
                var.set("—")
            self._update_button_states()
            return

        self.selected_profile_var.set(f"📁 {profile.name}")

        if profile.credential:
            # Status indicator
            if profile.is_active:
                self.status_indicator_var.set("🟢 ATIVO")
            elif profile.has_valid_credentials():
                self.status_indicator_var.set("⚪ Disponível")
            else:
                self.status_indicator_var.set("🔴 Expirado")

            # Details
            self.detail_vars['subscription'].set(
                StatusFormatter.format_subscription_type(
                    profile.credential.claude_ai_oauth.subscription_type
                )
            )
            self.detail_vars['expires'].set(
                TimeFormatter.format_expires_in_hours(
                    profile.credential.claude_ai_oauth.expires_in_hours()
                )
            )
            self.detail_vars['scopes'].set(
                StatusFormatter.format_scopes(
                    profile.credential.claude_ai_oauth.scopes
                )
            )
            self.detail_vars['rate_limit'].set(
                StatusFormatter.format_rate_limit_tier(
                    profile.credential.claude_ai_oauth.rate_limit_tier
                )
            )
        else:
            self.status_indicator_var.set("❌ Sem credenciais")
            for var in self.detail_vars.values():
                var.set("Indisponível")

        self._update_button_states()

    def _update_header_info(self):
        """Update header information."""
        self.profile_count_var.set(f"{len(self.profiles)} perfis")

        active_profile = ProfileManager.get_active_profile()
        if active_profile:
            self.active_profile_var.set(f"Ativo: {active_profile.name}")
        else:
            self.active_profile_var.set("Nenhum ativo")

    def _update_button_states(self):
        """Update button states based on selection."""
        if hasattr(self, 'switch_button'):
            if self.selected_profile and self.selected_profile.has_valid_credentials():
                self.switch_button.configure(state="normal")
            else:
                self.switch_button.configure(state="disabled")

    def _update_status(self, message: str):
        """Update the status bar message."""
        self.status_var.set(message)
        self.root.update_idletasks()

    # Action methods (reuse from original main_window.py with minor updates)
    def _refresh_profiles(self):
        """Refresh the profile list."""
        self._load_profiles()

    def _switch_to_selected_profile(self):
        """Switch to the currently selected profile."""
        if not self.selected_profile:
            messagebox.showwarning("Aviso", "Por favor, selecione um perfil para ativar.")
            return

        if not self.selected_profile.has_valid_credentials():
            result = messagebox.askyesno(
                "Credenciais Expiradas",
                f"O perfil '{self.selected_profile.name}' tem credenciais expiradas. "
                "Deseja ativar mesmo assim?"
            )
            if not result:
                return

        try:
            self._update_status(f"Ativando perfil: {self.selected_profile.name}")

            success = self.profile_manager.switch_to_profile(self.selected_profile.name)

            if success:
                self._update_status(f"Perfil ativado: {self.selected_profile.name}")
                messagebox.showinfo(
                    "Sucesso",
                    f"Perfil '{self.selected_profile.name}' ativado com sucesso!"
                )
                self._refresh_profiles()
            else:
                self._update_status("Falha ao ativar perfil")
                messagebox.showerror(
                    "Erro",
                    f"Falha ao ativar perfil '{self.selected_profile.name}'"
                )

        except Exception as e:
            self._update_status(f"Erro ao ativar perfil: {str(e)}")
            messagebox.showerror("Erro", f"Erro ao ativar perfil: {str(e)}")

    def _save_current_as_profile(self):
        """Save current active credentials as a new profile."""
        profile_name = simpledialog.askstring(
            "Salvar Perfil Atual",
            "Digite um nome para o novo perfil:"
        )

        if not profile_name:
            return

        is_valid, error_msg = ProfileValidator.validate_profile_name(profile_name)
        if not is_valid:
            messagebox.showerror("Nome de Perfil Inválido", error_msg)
            return

        existing_profiles = [p.name for p in self.profiles]
        if profile_name in existing_profiles:
            result = messagebox.askyesno(
                "Perfil Já Existe",
                f"O perfil '{profile_name}' já existe. Deseja sobrescrever?"
            )
            if not result:
                return

        try:
            self._update_status(f"Salvando credenciais como perfil: {profile_name}")

            success = self.profile_manager.save_current_as_profile(
                profile_name,
                overwrite=True
            )

            if success:
                self._update_status(f"Perfil salvo: {profile_name}")
                messagebox.showinfo(
                    "Sucesso",
                    f"Credenciais atuais salvas como perfil '{profile_name}'"
                )
                self._refresh_profiles()
            else:
                self._update_status("Falha ao salvar perfil")
                messagebox.showerror(
                    "Erro",
                    f"Falha ao salvar perfil '{profile_name}'"
                )

        except Exception as e:
            self._update_status(f"Erro ao salvar perfil: {str(e)}")
            messagebox.showerror("Erro", f"Erro ao salvar perfil: {str(e)}")

    def _rename_selected_profile(self):
        """Rename the currently selected profile."""
        if not self.selected_profile:
            messagebox.showwarning("Aviso", "Por favor, selecione um perfil para renomear.")
            return

        new_name = simpledialog.askstring(
            "Renomear Perfil",
            f"Digite o novo nome para '{self.selected_profile.name}':",
            initialvalue=self.selected_profile.name
        )

        if not new_name or new_name == self.selected_profile.name:
            return

        is_valid, error_msg = ProfileValidator.validate_profile_name(new_name)
        if not is_valid:
            messagebox.showerror("Nome de Perfil Inválido", error_msg)
            return

        try:
            self._update_status(f"Renomeando perfil: {self.selected_profile.name} → {new_name}")

            success = self.profile_manager.rename_profile(self.selected_profile.name, new_name)

            if success:
                self._update_status(f"Perfil renomeado: {new_name}")
                messagebox.showinfo(
                    "Sucesso",
                    f"Perfil renomeado para '{new_name}'"
                )
                self._refresh_profiles()
            else:
                self._update_status("Falha ao renomear perfil")
                messagebox.showerror(
                    "Erro",
                    f"Falha ao renomear perfil '{self.selected_profile.name}'"
                )

        except Exception as e:
            self._update_status(f"Erro ao renomear perfil: {str(e)}")
            messagebox.showerror("Erro", f"Erro ao renomear perfil: {str(e)}")

    def _delete_selected_profile(self):
        """Delete the currently selected profile."""
        if not self.selected_profile:
            messagebox.showwarning("Aviso", "Por favor, selecione um perfil para excluir.")
            return

        result = messagebox.askyesno(
            "Confirmar Exclusão",
            f"Tem certeza de que deseja excluir o perfil '{self.selected_profile.name}'?\n\n"
            "Esta ação não pode ser desfeita."
        )

        if not result:
            return

        try:
            self._update_status(f"Excluindo perfil: {self.selected_profile.name}")

            success = self.profile_manager.delete_profile(self.selected_profile.name)

            if success:
                self._update_status(f"Perfil excluído: {self.selected_profile.name}")
                messagebox.showinfo(
                    "Sucesso",
                    f"Perfil '{self.selected_profile.name}' excluído"
                )
                self.selected_profile = None
                self._update_profile_display(None)
                self._refresh_profiles()
            else:
                self._update_status("Falha ao excluir perfil")
                messagebox.showerror(
                    "Erro",
                    f"Falha ao excluir perfil '{self.selected_profile.name}'"
                )

        except Exception as e:
            self._update_status(f"Erro ao excluir perfil: {str(e)}")
            messagebox.showerror("Erro", f"Erro ao excluir perfil: {str(e)}")

    def _show_about(self):
        """Show the about dialog."""
        about_text = (
            "Claude Profile Manager v2.0\n"
            "Interface Moderna\n\n"
            "Gerencie facilmente seus perfis de autenticação do Claude CLI.\n"
            "Alterne rapidamente entre diferentes contas e sessões.\n\n"
            "✨ Funcionalidades:\n"
            "• Interface moderna e intuitiva\n"
            "• Troca rápida entre perfis\n"
            "• Visualização de status em tempo real\n"
            "• Gerenciamento seguro de credenciais\n"
            "• Validação automática de tokens\n\n"
            "Desenvolvido com Python e tkinter."
        )

        messagebox.showinfo("Sobre o Claude Profile Manager", about_text)

    def run(self):
        """Run the application main loop."""
        try:
            # Validate environment
            env_info = self.profile_manager.validate_environment()
            if not env_info['exists']:
                messagebox.showwarning(
                    "Diretório Claude Não Encontrado",
                    f"Diretório Claude não encontrado em: {env_info['path']}\n\n"
                    "Certifique-se de que o Claude CLI esteja instalado e tenha sido usado pelo menos uma vez."
                )

            self.root.mainloop()

        except KeyboardInterrupt:
            self.root.quit()
        except Exception as e:
            messagebox.showerror("Erro da Aplicação", f"Erro inesperado: {str(e)}")
        finally:
            try:
                self.root.destroy()
            except:
                pass


# Keep compatibility with original import
ClaudeProfileManagerApp = ModernClaudeProfileManagerApp
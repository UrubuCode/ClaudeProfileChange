"""
Simple and Clean Main Window for Claude Profile Manager

Clean, responsive interface that adapts to screen size with functional buttons.
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from typing import Optional, List
from models.profile import Profile
from services.profile_manager import ProfileManager
from utils.validators import ProfileValidator
from utils.formatters import StatusFormatter, TimeFormatter


class SimpleClaudeProfileManagerApp:
    """Simple and clean version of Claude Profile Manager."""

    def __init__(self):
        """Initialize the application with clean design."""
        self.root = tk.Tk()
        self.profile_manager = ProfileManager()
        self.selected_profile: Optional[Profile] = None
        self.profiles: List[Profile] = []

        self._setup_window()
        self._create_widgets()
        self._load_profiles()

    def _setup_window(self):
        """Setup responsive main window."""
        self.root.title("Claude Profile Manager v2.0")

        # Get screen dimensions
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        # Calculate responsive size (80% of screen, with reasonable limits)
        window_width = min(max(int(screen_width * 0.8), 900), 1400)
        window_height = min(max(int(screen_height * 0.8), 600), 1000)

        # Center window
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2

        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.root.minsize(800, 600)

        # Configure responsive layout
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        # Clean background
        self.root.configure(bg='#f8f9fa')

    def _create_widgets(self):
        """Create clean, functional widgets."""
        # Main container
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky="nsew")
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)

        # Header
        self._create_header(main_frame)

        # Content area
        content_frame = ttk.Frame(main_frame)
        content_frame.grid(row=1, column=0, sticky="nsew", pady=(20, 0))
        content_frame.columnconfigure(0, weight=1)
        content_frame.columnconfigure(1, weight=2)  # Main panel takes more space
        content_frame.rowconfigure(0, weight=1)

        # Left: Profile list
        self._create_profile_list_section(content_frame)

        # Right: Profile details
        self._create_profile_details_section(content_frame)

        # Footer
        self._create_footer(main_frame)

        # Menu
        self._create_menu()

    def _create_header(self, parent):
        """Create simple header."""
        header_frame = ttk.Frame(parent)
        header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        header_frame.columnconfigure(1, weight=1)

        # Title
        title_label = ttk.Label(
            header_frame,
            text="Claude Profile Manager",
            font=("Segoe UI", 16, "bold")
        )
        title_label.grid(row=0, column=0, sticky="w")

        # Info
        info_frame = ttk.Frame(header_frame)
        info_frame.grid(row=0, column=1, sticky="e")

        self.profile_count_var = tk.StringVar(value="0 perfis")
        ttk.Label(info_frame, textvariable=self.profile_count_var).pack(side="right")

    def _create_profile_list_section(self, parent):
        """Create profile list section."""
        # Left panel
        left_frame = ttk.LabelFrame(parent, text="Perfis Disponíveis", padding="10")
        left_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        left_frame.columnconfigure(0, weight=1)
        left_frame.rowconfigure(0, weight=1)

        # Treeview for profiles
        tree_frame = ttk.Frame(left_frame)
        tree_frame.grid(row=0, column=0, sticky="nsew", pady=(0, 10))
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)

        # Simple treeview
        columns = ("status", "expires")
        self.tree = ttk.Treeview(
            tree_frame,
            columns=columns,
            show="tree headings",
            height=15
        )

        # Configure columns
        self.tree.heading("#0", text="Nome do Perfil")
        self.tree.heading("status", text="Status")
        self.tree.heading("expires", text="Expira em")

        self.tree.column("#0", width=150)
        self.tree.column("status", width=80)
        self.tree.column("expires", width=80)

        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        # Events
        self.tree.bind("<<TreeviewSelect>>", self._on_profile_select)
        self.tree.bind("<Double-1>", self._on_profile_double_click)

        # Action buttons
        button_frame = ttk.Frame(left_frame)
        button_frame.grid(row=1, column=0, sticky="ew")
        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)

        ttk.Button(
            button_frame,
            text="Salvar Atual",
            command=self._save_current_profile
        ).grid(row=0, column=0, sticky="ew", padx=(0, 5))

        ttk.Button(
            button_frame,
            text="Atualizar",
            command=self._refresh_profiles
        ).grid(row=0, column=1, sticky="ew", padx=(5, 0))

    def _create_profile_details_section(self, parent):
        """Create profile details section."""
        # Right panel
        right_frame = ttk.LabelFrame(parent, text="Detalhes do Perfil", padding="15")
        right_frame.grid(row=0, column=1, sticky="nsew")
        right_frame.columnconfigure(0, weight=1)
        right_frame.rowconfigure(1, weight=1)

        # Profile name
        name_frame = ttk.Frame(right_frame)
        name_frame.grid(row=0, column=0, sticky="ew", pady=(0, 15))
        name_frame.columnconfigure(1, weight=1)

        ttk.Label(name_frame, text="Perfil Selecionado:", font=("Segoe UI", 10, "bold")).grid(row=0, column=0, sticky="w")

        self.selected_profile_var = tk.StringVar(value="Nenhum selecionado")
        ttk.Label(name_frame, textvariable=self.selected_profile_var, font=("Segoe UI", 12)).grid(row=0, column=1, sticky="w", padx=(10, 0))

        # Details
        details_frame = ttk.Frame(right_frame)
        details_frame.grid(row=1, column=0, sticky="nsew", pady=(0, 15))

        # Detail variables
        self.detail_vars = {
            'status': tk.StringVar(value="—"),
            'subscription': tk.StringVar(value="—"),
            'expires': tk.StringVar(value="—"),
            'scopes': tk.StringVar(value="—")
        }

        # Detail labels
        details_info = [
            ("Status:", self.detail_vars['status']),
            ("Assinatura:", self.detail_vars['subscription']),
            ("Expira em:", self.detail_vars['expires']),
            ("Escopos:", self.detail_vars['scopes'])
        ]

        for i, (label_text, var) in enumerate(details_info):
            ttk.Label(details_frame, text=label_text, font=("Segoe UI", 9, "bold")).grid(
                row=i, column=0, sticky="w", pady=5, padx=(0, 10)
            )
            ttk.Label(details_frame, textvariable=var, font=("Segoe UI", 9)).grid(
                row=i, column=1, sticky="w", pady=5
            )

        # Action buttons
        action_frame = ttk.Frame(right_frame)
        action_frame.grid(row=2, column=0, sticky="ew")

        # Button frame for better layout
        btn_frame = ttk.Frame(action_frame)
        btn_frame.pack(fill="x")

        self.switch_btn = ttk.Button(
            btn_frame,
            text="Ativar Perfil",
            command=self._switch_profile,
            state="disabled"
        )
        self.switch_btn.pack(side="left", padx=(0, 10))

        self.rename_btn = ttk.Button(
            btn_frame,
            text="Renomear",
            command=self._rename_profile,
            state="disabled"
        )
        self.rename_btn.pack(side="left", padx=(0, 10))

        self.delete_btn = ttk.Button(
            btn_frame,
            text="Excluir",
            command=self._delete_profile,
            state="disabled"
        )
        self.delete_btn.pack(side="left")

    def _create_footer(self, parent):
        """Create simple footer with status."""
        footer_frame = ttk.Frame(parent)
        footer_frame.grid(row=2, column=0, sticky="ew", pady=(20, 0))

        ttk.Separator(footer_frame, orient="horizontal").pack(fill="x", pady=(0, 10))

        self.status_var = tk.StringVar(value="Pronto")
        status_label = ttk.Label(footer_frame, textvariable=self.status_var, font=("Segoe UI", 9))
        status_label.pack(anchor="w")

    def _create_menu(self):
        """Create simple menu."""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Arquivo", menu=file_menu)
        file_menu.add_command(label="Atualizar", command=self._refresh_profiles)
        file_menu.add_separator()
        file_menu.add_command(label="Sair", command=self.root.quit)

        # Profile menu
        profile_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Perfil", menu=profile_menu)
        profile_menu.add_command(label="Ativar", command=self._switch_profile)
        profile_menu.add_command(label="Salvar Atual", command=self._save_current_profile)
        profile_menu.add_separator()
        profile_menu.add_command(label="Renomear", command=self._rename_profile)
        profile_menu.add_command(label="Excluir", command=self._delete_profile)

        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Ajuda", menu=help_menu)
        help_menu.add_command(label="Sobre", command=self._show_about)

    # Event handlers
    def _on_profile_select(self, event):
        """Handle profile selection."""
        selection = self.tree.selection()
        if not selection:
            self.selected_profile = None
            self._update_details_display(None)
            return

        item = selection[0]
        profile_name = self.tree.item(item, "text")
        self.selected_profile = next(
            (p for p in self.profiles if p.name == profile_name), None
        )
        self._update_details_display(self.selected_profile)

    def _on_profile_double_click(self, event):
        """Handle double click to activate profile."""
        if self.selected_profile:
            self._switch_profile()

    # Core functionality
    def _load_profiles(self):
        """Load all profiles."""
        try:
            self._update_status("Carregando perfis...")
            self.profiles = self.profile_manager.get_all_profiles()
            self._update_profile_list()
            self._update_header_info()
            self._update_status(f"Carregados {len(self.profiles)} perfis")
        except Exception as e:
            self._update_status(f"Erro ao carregar perfis: {str(e)}")
            messagebox.showerror("Erro", f"Erro ao carregar perfis: {str(e)}")

    def _update_profile_list(self):
        """Update the profile list."""
        # Clear existing
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Add profiles
        for profile in self.profiles:
            if profile.is_active:
                status = "🟢 Ativo"
            elif profile.has_valid_credentials():
                status = "⚪ Disponível"
            else:
                status = "🔴 Expirado"

            expires_text = "—"
            if profile.credential:
                expires_text = TimeFormatter.format_expires_in_hours(
                    profile.credential.claude_ai_oauth.expires_in_hours()
                )

            self.tree.insert(
                "",
                "end",
                text=profile.name,
                values=(status, expires_text)
            )

    def _update_details_display(self, profile: Optional[Profile]):
        """Update profile details display."""
        if profile is None:
            self.selected_profile_var.set("Nenhum selecionado")
            for var in self.detail_vars.values():
                var.set("—")
            self._update_button_states(False)
            return

        self.selected_profile_var.set(profile.name)

        if profile.credential:
            # Status
            if profile.is_active:
                status = "🟢 Ativo"
            elif profile.has_valid_credentials():
                status = "⚪ Disponível"
            else:
                status = "🔴 Expirado"
            self.detail_vars['status'].set(status)

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
        else:
            for var in self.detail_vars.values():
                var.set("Sem credenciais")

        self._update_button_states(True)

    def _update_button_states(self, enabled: bool):
        """Update button states."""
        state = "normal" if enabled else "disabled"

        # Enable switch only if profile has valid credentials
        if enabled and self.selected_profile and self.selected_profile.has_valid_credentials():
            self.switch_btn.configure(state="normal")
        else:
            self.switch_btn.configure(state="disabled")

        self.rename_btn.configure(state=state)
        self.delete_btn.configure(state=state)

    def _update_header_info(self):
        """Update header information."""
        self.profile_count_var.set(f"{len(self.profiles)} perfis")

    def _update_status(self, message: str):
        """Update status message."""
        self.status_var.set(message)
        self.root.update_idletasks()

    # Actions
    def _refresh_profiles(self):
        """Refresh profiles."""
        self._load_profiles()

    def _switch_profile(self):
        """Switch to selected profile."""
        if not self.selected_profile:
            messagebox.showwarning("Aviso", "Selecione um perfil primeiro.")
            return

        if not self.selected_profile.has_valid_credentials():
            result = messagebox.askyesno(
                "Credenciais Expiradas",
                f"O perfil '{self.selected_profile.name}' tem credenciais expiradas. "
                "Ativar mesmo assim?"
            )
            if not result:
                return

        try:
            self._update_status(f"Ativando perfil: {self.selected_profile.name}")

            success = self.profile_manager.switch_to_profile(self.selected_profile.name)

            if success:
                self._update_status("Perfil ativado com sucesso!")
                messagebox.showinfo("Sucesso", f"Perfil '{self.selected_profile.name}' ativado!")
                self._refresh_profiles()
            else:
                self._update_status("Erro ao ativar perfil")
                messagebox.showerror("Erro", "Falha ao ativar o perfil.")

        except Exception as e:
            self._update_status(f"Erro: {str(e)}")
            messagebox.showerror("Erro", f"Erro ao ativar perfil: {str(e)}")

    def _save_current_profile(self):
        """Save current credentials as new profile."""
        name = simpledialog.askstring(
            "Salvar Perfil",
            "Digite o nome do novo perfil:"
        )

        if not name:
            return

        is_valid, error_msg = ProfileValidator.validate_profile_name(name)
        if not is_valid:
            messagebox.showerror("Nome Inválido", error_msg)
            return

        # Check if exists
        existing_names = [p.name for p in self.profiles]
        if name in existing_names:
            result = messagebox.askyesno(
                "Perfil Existe",
                f"O perfil '{name}' já existe. Sobrescrever?"
            )
            if not result:
                return

        try:
            self._update_status(f"Salvando perfil: {name}")

            success = self.profile_manager.save_current_as_profile(name, overwrite=True)

            if success:
                self._update_status("Perfil salvo com sucesso!")
                messagebox.showinfo("Sucesso", f"Perfil '{name}' salvo!")
                self._refresh_profiles()
            else:
                self._update_status("Erro ao salvar perfil")
                messagebox.showerror("Erro", "Falha ao salvar o perfil.")

        except Exception as e:
            self._update_status(f"Erro: {str(e)}")
            messagebox.showerror("Erro", f"Erro ao salvar perfil: {str(e)}")

    def _rename_profile(self):
        """Rename selected profile."""
        if not self.selected_profile:
            messagebox.showwarning("Aviso", "Selecione um perfil primeiro.")
            return

        new_name = simpledialog.askstring(
            "Renomear Perfil",
            f"Novo nome para '{self.selected_profile.name}':",
            initialvalue=self.selected_profile.name
        )

        if not new_name or new_name == self.selected_profile.name:
            return

        is_valid, error_msg = ProfileValidator.validate_profile_name(new_name)
        if not is_valid:
            messagebox.showerror("Nome Inválido", error_msg)
            return

        try:
            self._update_status(f"Renomeando perfil: {self.selected_profile.name}")

            success = self.profile_manager.rename_profile(self.selected_profile.name, new_name)

            if success:
                self._update_status("Perfil renomeado com sucesso!")
                messagebox.showinfo("Sucesso", f"Perfil renomeado para '{new_name}'!")
                self._refresh_profiles()
            else:
                self._update_status("Erro ao renomear perfil")
                messagebox.showerror("Erro", "Falha ao renomear o perfil.")

        except Exception as e:
            self._update_status(f"Erro: {str(e)}")
            messagebox.showerror("Erro", f"Erro ao renomear perfil: {str(e)}")

    def _delete_profile(self):
        """Delete selected profile."""
        if not self.selected_profile:
            messagebox.showwarning("Aviso", "Selecione um perfil primeiro.")
            return

        result = messagebox.askyesno(
            "Confirmar Exclusão",
            f"Tem certeza que deseja excluir o perfil '{self.selected_profile.name}'?\n\n"
            "Esta ação não pode ser desfeita."
        )

        if not result:
            return

        try:
            self._update_status(f"Excluindo perfil: {self.selected_profile.name}")

            success = self.profile_manager.delete_profile(self.selected_profile.name)

            if success:
                self._update_status("Perfil excluído com sucesso!")
                messagebox.showinfo("Sucesso", f"Perfil '{self.selected_profile.name}' excluído!")
                self.selected_profile = None
                self._update_details_display(None)
                self._refresh_profiles()
            else:
                self._update_status("Erro ao excluir perfil")
                messagebox.showerror("Erro", "Falha ao excluir o perfil.")

        except Exception as e:
            self._update_status(f"Erro: {str(e)}")
            messagebox.showerror("Erro", f"Erro ao excluir perfil: {str(e)}")

    def _show_about(self):
        """Show about dialog."""
        about_text = (
            "Claude Profile Manager v2.0\n"
            "Interface Simples e Funcional\n\n"
            "Gerencie seus perfis de autenticação do Claude CLI\n"
            "de forma rápida e intuitiva.\n\n"
            "Funcionalidades:\n"
            "• Troca rápida entre perfis\n"
            "• Interface responsiva\n"
            "• Validação automática\n"
            "• Design limpo e funcional\n\n"
            "Desenvolvido com Python e tkinter."
        )
        messagebox.showinfo("Sobre", about_text)

    def run(self):
        """Run the application."""
        try:
            env_info = self.profile_manager.validate_environment()
            if not env_info['exists']:
                messagebox.showwarning(
                    "Claude CLI Não Encontrado",
                    f"Diretório Claude não encontrado em: {env_info['path']}\n\n"
                    "Certifique-se de que o Claude CLI esteja instalado."
                )

            self.root.mainloop()

        except KeyboardInterrupt:
            self.root.quit()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro inesperado: {str(e)}")
        finally:
            try:
                self.root.destroy()
            except:
                pass


# Use simple version as default
ClaudeProfileManagerApp = SimpleClaudeProfileManagerApp
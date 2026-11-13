//! Perfis do Claude CLI baseados em `CLAUDE_CONFIG_DIR`.
//!
//! Cada perfil é uma pasta própria em `~/.claude-profiles/<nome>/`, com seu
//! próprio `.credentials.json` e `.claude.json`. Nada é copiado entre contas:
//! o CLI renova o token dentro da pasta da conta, então a sessão nunca fica
//! desatualizada. O perfil "padrão" é o `~/.claude` original (variável ausente).
//!
//! Trocar o perfil padrão = gravar `CLAUDE_CONFIG_DIR` no ambiente do usuário.

use serde::{Deserialize, Serialize};
use std::fs;
use std::path::{Path, PathBuf};

pub const DEFAULT_NAME: &str = "padrão";

/// Itens do `~/.claude` principal compartilhados com todos os perfis via junction.
const SHARED_DIRS: &[&str] = &["skills", "plugins", "agents", "commands"];
/// Arquivos copiados uma vez na criação (junction só funciona com pastas).
const COPIED_FILES: &[&str] = &["settings.json", "CLAUDE.md"];

#[derive(Debug, Deserialize, Default)]
#[serde(rename_all = "camelCase")]
struct OAuth {
    #[serde(default)]
    refresh_token: String,
    #[serde(default)]
    expires_at: i64,
    #[serde(default)]
    refresh_token_expires_at: Option<i64>,
    #[serde(default)]
    scopes: Vec<String>,
    #[serde(default)]
    subscription_type: Option<String>,
    #[serde(default)]
    rate_limit_tier: Option<String>,
}

#[derive(Debug, Deserialize)]
#[serde(rename_all = "camelCase")]
struct Credentials {
    claude_ai_oauth: Option<OAuth>,
}

#[derive(Debug, Deserialize, Default)]
#[serde(rename_all = "camelCase")]
struct Account {
    email_address: Option<String>,
    display_name: Option<String>,
    organization_name: Option<String>,
    plan_display_name: Option<String>,
}

#[derive(Debug, Deserialize)]
#[serde(rename_all = "camelCase")]
struct GlobalConfig {
    oauth_account: Option<Account>,
}

#[derive(Debug, Serialize, Clone)]
#[serde(rename_all = "camelCase")]
pub struct ProfileInfo {
    pub name: String,
    pub path: String,
    pub is_default_profile: bool,
    /// É o perfil que `CLAUDE_CONFIG_DIR` (do usuário) aponta hoje.
    pub is_selected: bool,
    pub logged_in: bool,
    pub email: Option<String>,
    pub display_name: Option<String>,
    pub organization: Option<String>,
    pub plan: Option<String>,
    pub subscription_type: Option<String>,
    pub rate_limit_tier: Option<String>,
    pub scopes: Vec<String>,
    pub has_refresh_token: bool,
    pub expires_at: i64,
    pub refresh_expires_at: Option<i64>,
    pub error: Option<String>,
}

#[derive(Debug, Serialize)]
#[serde(rename_all = "camelCase")]
pub struct State {
    pub profiles_root: String,
    /// Valor atual de CLAUDE_CONFIG_DIR no ambiente do usuário (None = padrão).
    pub env_value: Option<String>,
    /// A variável aponta para uma pasta que não é nenhum perfil conhecido.
    pub env_unknown: bool,
    pub profiles: Vec<ProfileInfo>,
    /// Menu "Abrir Claude aqui" instalado no Explorer (preenchido pelo app).
    pub explorer_menu: bool,
}

pub struct Store {
    home: PathBuf,
    root: PathBuf,
}

pub fn validate_name(name: &str) -> Result<String, String> {
    let n = name.trim();
    if n.is_empty() {
        return Err("O nome do perfil não pode ser vazio.".into());
    }
    if n.chars().count() > 48 {
        return Err("O nome do perfil deve ter no máximo 48 caracteres.".into());
    }
    if n.starts_with('.') || n.ends_with('.') || n.ends_with(' ') {
        return Err("O nome não pode começar ou terminar com ponto ou espaço.".into());
    }
    if n.eq_ignore_ascii_case(DEFAULT_NAME) || n.eq_ignore_ascii_case("padrao") {
        return Err(format!("'{DEFAULT_NAME}' é reservado para o ~/.claude original."));
    }
    if !n.chars().all(|c| c.is_alphanumeric() || matches!(c, '-' | '_' | ' ')) {
        return Err("Use apenas letras, números, espaço, '-' ou '_'.".into());
    }
    Ok(n.to_string())
}

fn norm(p: &Path) -> String {
    let s = p.to_string_lossy().replace('/', "\\");
    s.trim_end_matches('\\').to_lowercase()
}

fn read_json<T: for<'de> Deserialize<'de>>(p: &Path) -> Result<Option<T>, String> {
    match fs::read(p) {
        Ok(b) => serde_json::from_slice(&b)
            .map(Some)
            .map_err(|e| format!("{} inválido: {e}", p.file_name().unwrap_or_default().to_string_lossy())),
        Err(_) => Ok(None),
    }
}

/// Remove links (junctions/symlinks) sem seguir para o destino.
fn remove_link(p: &Path) -> std::io::Result<()> {
    fs::remove_dir(p).or_else(|_| fs::remove_file(p))
}

fn is_link(p: &Path) -> bool {
    fs::symlink_metadata(p).map(|m| m.file_type().is_symlink()).unwrap_or(false)
        || junction_target(p).is_some()
}

#[cfg(windows)]
fn junction_target(p: &Path) -> Option<PathBuf> {
    junction::get_target(p).ok()
}
#[cfg(not(windows))]
fn junction_target(_p: &Path) -> Option<PathBuf> {
    None
}

#[cfg(windows)]
fn make_dir_link(target: &Path, link: &Path) -> std::io::Result<()> {
    junction::create(target, link)
}
#[cfg(not(windows))]
fn make_dir_link(target: &Path, link: &Path) -> std::io::Result<()> {
    std::os::unix::fs::symlink(target, link)
}

impl Store {
    pub fn new(home: PathBuf) -> Self {
        let root = home.join(".claude-profiles");
        Self { home, root }
    }

    pub fn from_env() -> Self {
        Self::new(dirs::home_dir().unwrap_or_default())
    }

    fn default_dir(&self) -> PathBuf {
        self.home.join(".claude")
    }

    pub fn dir_of(&self, name: &str) -> Result<PathBuf, String> {
        if name == DEFAULT_NAME {
            return Ok(self.default_dir());
        }
        let n = validate_name(name)?;
        let d = self.root.join(&n);
        if !d.is_dir() {
            return Err(format!("O perfil '{n}' não existe."));
        }
        Ok(d)
    }

    /// Valor que `CLAUDE_CONFIG_DIR` deve ter para o perfil (None = remover variável).
    pub fn env_for(&self, name: &str) -> Result<Option<String>, String> {
        if name == DEFAULT_NAME {
            return Ok(None);
        }
        Ok(Some(self.dir_of(name)?.to_string_lossy().into_owned()))
    }

    fn info(&self, name: &str, dir: &Path, global_cfg: &Path, env: Option<&str>) -> ProfileInfo {
        let is_default = name == DEFAULT_NAME;
        let is_selected = match env {
            None => is_default,
            Some(v) => norm(Path::new(v)) == norm(dir),
        };
        let mut errors = vec![];
        let cred = read_json::<Credentials>(&dir.join(".credentials.json"))
            .unwrap_or_else(|e| { errors.push(e); None })
            .and_then(|c| c.claude_ai_oauth);
        let acct = read_json::<GlobalConfig>(global_cfg)
            .unwrap_or_else(|e| { errors.push(e); None })
            .and_then(|g| g.oauth_account)
            .unwrap_or_default();
        let o = cred.as_ref();
        ProfileInfo {
            name: name.into(),
            path: dir.display().to_string(),
            is_default_profile: is_default,
            is_selected,
            logged_in: o.is_some(),
            email: acct.email_address,
            display_name: acct.display_name,
            organization: acct.organization_name,
            plan: acct.plan_display_name,
            subscription_type: o.and_then(|o| o.subscription_type.clone()),
            rate_limit_tier: o.and_then(|o| o.rate_limit_tier.clone()),
            scopes: o.map(|o| o.scopes.clone()).unwrap_or_default(),
            has_refresh_token: o.is_some_and(|o| !o.refresh_token.is_empty()),
            expires_at: o.map(|o| o.expires_at).unwrap_or(0),
            refresh_expires_at: o.and_then(|o| o.refresh_token_expires_at),
            error: (!errors.is_empty()).then(|| errors.join("; ")),
        }
    }

    pub fn state(&self, env: Option<String>) -> State {
        let env = env.filter(|v| !v.trim().is_empty());
        let mut profiles = vec![self.info(
            DEFAULT_NAME,
            &self.default_dir(),
            &self.home.join(".claude.json"),
            env.as_deref(),
        )];
        let mut names: Vec<String> = fs::read_dir(&self.root)
            .map(|rd| {
                rd.filter_map(|e| e.ok())
                    .filter(|e| e.file_type().map(|t| t.is_dir()).unwrap_or(false))
                    .filter_map(|e| e.file_name().into_string().ok())
                    .collect()
            })
            .unwrap_or_default();
        names.sort_by_key(|n| n.to_lowercase());
        for n in names {
            let d = self.root.join(&n);
            let cfg = d.join(".claude.json");
            profiles.push(self.info(&n, &d, &cfg, env.as_deref()));
        }
        let env_unknown = env.is_some() && !profiles.iter().any(|p| p.is_selected);
        State {
            profiles_root: self.root.display().to_string(),
            env_value: env,
            env_unknown,
            profiles,
            explorer_menu: false,
        }
    }

    /// Cria a pasta do perfil e compartilha configurações do ~/.claude principal.
    /// Retorna avisos não fatais (ex.: link que não pôde ser criado).
    pub fn create(&self, name: &str) -> Result<(String, Vec<String>), String> {
        let n = validate_name(name)?;
        let dir = self.root.join(&n);
        if dir.exists() {
            return Err(format!("O perfil '{n}' já existe."));
        }
        fs::create_dir_all(&dir).map_err(|e| format!("Não foi possível criar {}: {e}", dir.display()))?;
        let main = self.default_dir();
        let mut warnings = vec![];
        for d in SHARED_DIRS {
            let src = main.join(d);
            if src.is_dir() {
                if let Err(e) = make_dir_link(&src, &dir.join(d)) {
                    warnings.push(format!("não foi possível ligar '{d}': {e}"));
                }
            }
        }
        for f in COPIED_FILES {
            let src = main.join(f);
            if src.is_file() {
                if let Err(e) = fs::copy(&src, dir.join(f)) {
                    warnings.push(format!("não foi possível copiar '{f}': {e}"));
                }
            }
        }
        Ok((n, warnings))
    }

    pub fn rename(&self, old: &str, new: &str) -> Result<String, String> {
        if old == DEFAULT_NAME {
            return Err("O perfil padrão não pode ser renomeado.".into());
        }
        let from = self.dir_of(old)?;
        let n = validate_name(new)?;
        let to = self.root.join(&n);
        if to.exists() && !old.eq_ignore_ascii_case(&n) {
            return Err(format!("O perfil '{n}' já existe."));
        }
        fs::rename(&from, &to).map_err(|e| {
            format!("Não foi possível renomear (feche os terminais do Claude que usam esse perfil): {e}")
        })?;
        Ok(n)
    }

    /// Exclui a pasta do perfil. Links compartilhados são removidos antes,
    /// para nunca apagar o conteúdo do ~/.claude principal.
    pub fn delete(&self, name: &str) -> Result<(), String> {
        if name == DEFAULT_NAME {
            return Err("O perfil padrão não pode ser excluído.".into());
        }
        let dir = self.dir_of(name)?;
        if let Ok(rd) = fs::read_dir(&dir) {
            for e in rd.filter_map(|e| e.ok()) {
                let p = e.path();
                if is_link(&p) {
                    remove_link(&p).map_err(|e| format!("Falha ao remover link {}: {e}", p.display()))?;
                }
            }
        }
        fs::remove_dir_all(&dir).map_err(|e| {
            format!("Não foi possível excluir (feche os terminais do Claude que usam esse perfil): {e}")
        })
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn setup() -> (tempfile::TempDir, Store) {
        let d = tempfile::tempdir().unwrap();
        let main = d.path().join(".claude");
        fs::create_dir_all(main.join("skills/minha")).unwrap();
        fs::write(main.join("skills/minha/SKILL.md"), "x").unwrap();
        fs::write(main.join("settings.json"), "{}").unwrap();
        fs::write(
            main.join(".credentials.json"),
            r#"{"claudeAiOauth":{"accessToken":"a","refreshToken":"r","expiresAt":1,"scopes":["user:inference"],"subscriptionType":"max"},"mcpOAuth":{}}"#,
        )
        .unwrap();
        fs::write(
            d.path().join(".claude.json"),
            r#"{"oauthAccount":{"emailAddress":"a@x.com","organizationName":"Org"},"outro":1}"#,
        )
        .unwrap();
        let s = Store::new(d.path().to_path_buf());
        (d, s)
    }

    #[test]
    fn default_profile_reads_home_config() {
        let (_d, s) = setup();
        let st = s.state(None);
        assert_eq!(st.profiles.len(), 1);
        let p = &st.profiles[0];
        assert!(p.is_default_profile && p.is_selected && p.logged_in);
        assert_eq!(p.email.as_deref(), Some("a@x.com"));
        assert_eq!(p.subscription_type.as_deref(), Some("max"));
    }

    #[test]
    fn create_select_and_detect() {
        let (d, s) = setup();
        let (n, warns) = s.create("trabalho").unwrap();
        assert!(warns.is_empty(), "{warns:?}");
        let dir = d.path().join(".claude-profiles/trabalho");
        assert!(dir.join("skills/minha/SKILL.md").exists(), "skills compartilhadas");
        assert!(dir.join("settings.json").exists());
        let env = s.env_for(&n).unwrap();
        // CLAUDE_CONFIG_DIR com barra final e caixa diferente ainda casa
        let st = s.state(env.map(|e| e.to_uppercase() + "\\"));
        let p = st.profiles.iter().find(|p| p.name == "trabalho").unwrap();
        assert!(p.is_selected && !p.logged_in);
        assert!(!st.profiles[0].is_selected);
        assert!(!st.env_unknown);
        assert!(s.create("trabalho").is_err());
    }

    #[test]
    fn delete_keeps_shared_content() {
        let (d, s) = setup();
        s.create("x").unwrap();
        s.delete("x").unwrap();
        assert!(!d.path().join(".claude-profiles/x").exists());
        assert!(d.path().join(".claude/skills/minha/SKILL.md").exists(), "não pode apagar o original");
        assert!(s.delete(DEFAULT_NAME).is_err());
    }

    #[test]
    fn rename_and_unknown_env() {
        let (_d, s) = setup();
        s.create("a").unwrap();
        s.create("b").unwrap();
        assert!(s.rename("a", "b").is_err());
        assert_eq!(s.rename("a", "c").unwrap(), "c");
        assert!(s.dir_of("c").is_ok() && s.dir_of("a").is_err());
        assert!(s.state(Some("D:\\outro".into())).env_unknown);
    }

    #[test]
    fn rejects_bad_names() {
        for n in ["", " ", "../x", ".h", "a/b", "a\\b", "a:b", "padrão", "Padrao", "x."] {
            assert!(validate_name(n).is_err(), "{n}");
        }
        assert!(validate_name("meu perfil_1").is_ok());
    }
}

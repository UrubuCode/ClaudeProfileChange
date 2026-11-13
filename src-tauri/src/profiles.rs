//! Perfis por ferramenta (Claude Code, Codex, Antigravity).
//!
//! Cada perfil é uma pasta própria (ex.: `~/.claude-profiles/<nome>/`) que a
//! ferramenta usa como configuração, com o próprio login dentro. Nada é copiado
//! entre contas: a ferramenta renova o token dentro da pasta da conta, então a
//! sessão nunca fica desatualizada. O perfil "padrão" é a instalação original.

use crate::tools::Tool;
use serde::Serialize;
use std::fs;
use std::path::{Path, PathBuf};

pub const DEFAULT_NAME: &str = "padrão";

#[derive(Debug, Serialize, Clone)]
#[serde(rename_all = "camelCase")]
pub struct Detail {
    pub label: String,
    pub value: String,
}

#[derive(Debug, Serialize, Clone)]
#[serde(rename_all = "camelCase")]
pub struct ProfileInfo {
    pub tool: Tool,
    pub name: String,
    pub path: String,
    pub is_default_profile: bool,
    /// É o perfil que a variável da ferramenta (do usuário) aponta hoje.
    pub is_selected: bool,
    pub logged_in: bool,
    pub email: Option<String>,
    pub organization: Option<String>,
    pub plan: Option<String>,
    /// Validade do access token (ms) — quando a ferramenta informa.
    pub expires_at: Option<i64>,
    /// Validade do login/refresh token (ms) — quando a ferramenta informa.
    pub refresh_expires_at: Option<i64>,
    pub scopes: Vec<String>,
    /// Informações extras específicas da ferramenta.
    pub details: Vec<Detail>,
    pub error: Option<String>,
}

#[derive(Debug, Serialize)]
#[serde(rename_all = "camelCase")]
pub struct ToolState {
    pub tool: Tool,
    pub label: String,
    pub command: String,
    pub installed: bool,
    pub supports_default: bool,
    pub env_var: Option<String>,
    pub profiles_root: String,
    /// Valor atual da variável no ambiente do usuário (None = padrão).
    pub env_value: Option<String>,
    /// A variável aponta para uma pasta que não é nenhum perfil conhecido.
    pub env_unknown: bool,
    pub profiles: Vec<ProfileInfo>,
}

pub struct Store {
    pub tool: Tool,
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
        return Err(format!("'{DEFAULT_NAME}' é reservado para a instalação original."));
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

fn read_value(p: &Path) -> Result<Option<serde_json::Value>, String> {
    match fs::read(p) {
        Ok(b) => serde_json::from_slice(&b)
            .map(Some)
            .map_err(|e| format!("{} inválido: {e}", p.file_name().unwrap_or_default().to_string_lossy())),
        Err(_) => Ok(None),
    }
}

fn s(v: &serde_json::Value, k: &str) -> Option<String> {
    v.get(k).and_then(|x| x.as_str()).filter(|x| !x.is_empty()).map(String::from)
}

/// Payload (JSON) de um JWT, sem validar assinatura — só para exibir e-mail/plano.
fn jwt_payload(jwt: &str) -> Option<serde_json::Value> {
    use base64::Engine;
    let part = jwt.split('.').nth(1)?;
    let bytes = base64::engine::general_purpose::URL_SAFE_NO_PAD
        .decode(part.trim_end_matches('='))
        .ok()?;
    serde_json::from_slice(&bytes).ok()
}

/// Primeiro e-mail que aparece num arquivo de log (fallback do agy).
fn email_in_log(p: &Path) -> Option<String> {
    let text = fs::read_to_string(p).ok()?;
    text.split(|c: char| c.is_whitespace() || "\"'<>(),;[]=:".contains(c))
        .find(|w| {
            let mut parts = w.split('@');
            matches!((parts.next(), parts.next(), parts.next()), (Some(a), Some(b), None)
                if !a.is_empty() && b.contains('.') && !b.starts_with('.'))
        })
        .map(String::from)
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

/// Existe a credencial genérica no Gerenciador de Credenciais do Windows?
#[cfg(windows)]
fn has_windows_credential(target: &str) -> bool {
    use windows_sys::Win32::Security::Credentials::{CredFree, CredReadW, CREDENTIALW, CRED_TYPE_GENERIC};
    let w: Vec<u16> = target.encode_utf16().chain(Some(0)).collect();
    let mut out: *mut CREDENTIALW = std::ptr::null_mut();
    let ok = unsafe { CredReadW(w.as_ptr(), CRED_TYPE_GENERIC, 0, &mut out) } != 0;
    if ok {
        unsafe { CredFree(out as *const _) };
    }
    ok
}
#[cfg(not(windows))]
fn has_windows_credential(_target: &str) -> bool {
    false
}

impl Store {
    pub fn new(tool: Tool, home: PathBuf) -> Self {
        let root = tool.profiles_root(&home);
        Self { tool, home, root }
    }

    pub fn from_env(tool: Tool) -> Self {
        Self::new(tool, dirs::home_dir().unwrap_or_default())
    }

    fn default_dir(&self) -> PathBuf {
        self.tool.default_dir(&self.home)
    }

    pub fn dir_of(&self, name: &str) -> Result<PathBuf, String> {
        if name == DEFAULT_NAME {
            return Ok(self.default_dir());
        }
        let n = validate_name(name)?;
        let d = self.root.join(&n);
        if !d.is_dir() {
            return Err(format!("O perfil '{n}' de {} não existe.", self.tool.short()));
        }
        Ok(d)
    }

    /// Valor que a variável da ferramenta deve ter para o perfil (None = remover).
    pub fn env_for(&self, name: &str) -> Result<Option<String>, String> {
        if !self.tool.supports_default() {
            return Err(format!("{} não permite definir um perfil padrão do sistema.", self.tool.label()));
        }
        if name == DEFAULT_NAME {
            return Ok(None);
        }
        Ok(Some(self.dir_of(name)?.to_string_lossy().into_owned()))
    }

    /// Variáveis para abrir a ferramenta neste perfil.
    pub fn launch_env(&self, name: &str) -> Result<Vec<(&'static str, Option<String>)>, String> {
        let dir = self.dir_of(name)?;
        Ok(self.tool.launch_env(&dir, name == DEFAULT_NAME))
    }

    fn info(&self, name: &str, dir: &Path, env: Option<&str>) -> ProfileInfo {
        let is_default = name == DEFAULT_NAME;
        let is_selected = match (self.tool.supports_default(), env) {
            (false, _) => is_default,
            (true, None) => is_default,
            (true, Some(v)) => norm(Path::new(v)) == norm(dir),
        };
        let mut p = ProfileInfo {
            tool: self.tool,
            name: name.into(),
            path: dir.display().to_string(),
            is_default_profile: is_default,
            is_selected,
            logged_in: false,
            email: None,
            organization: None,
            plan: None,
            expires_at: None,
            refresh_expires_at: None,
            scopes: vec![],
            details: vec![],
            error: None,
        };
        let mut errors = vec![];
        match self.tool {
            Tool::Claude => self.fill_claude(&mut p, dir, is_default, &mut errors),
            Tool::Codex => Self::fill_codex(&mut p, dir, &mut errors),
            Tool::Agy => Self::fill_agy(&mut p, dir, is_default, &mut errors),
        }
        p.error = (!errors.is_empty()).then(|| errors.join("; "));
        p
    }

    fn fill_claude(&self, p: &mut ProfileInfo, dir: &Path, is_default: bool, errors: &mut Vec<String>) {
        // A conta (e-mail, organização) fica no .claude.json: na home para o
        // perfil padrão, dentro da pasta para os demais.
        let global = if is_default { self.home.join(".claude.json") } else { dir.join(".claude.json") };
        let cred = read_value(&dir.join(".credentials.json")).unwrap_or_else(|e| {
            errors.push(e);
            None
        });
        let o = cred.as_ref().and_then(|c| c.get("claudeAiOauth"));
        if let Some(o) = o {
            p.logged_in = true;
            p.expires_at = o.get("expiresAt").and_then(|x| x.as_i64());
            p.refresh_expires_at = o.get("refreshTokenExpiresAt").and_then(|x| x.as_i64());
            p.scopes = o
                .get("scopes")
                .and_then(|x| x.as_array())
                .map(|a| a.iter().filter_map(|x| x.as_str().map(String::from)).collect())
                .unwrap_or_default();
            p.plan = s(o, "subscriptionType").map(cap);
            if let Some(t) = s(o, "rateLimitTier") {
                p.details.push(Detail { label: "Rate limit tier".into(), value: t });
            }
            if s(o, "refreshToken").is_none() {
                p.details.push(Detail { label: "Refresh token".into(), value: "ausente".into() });
            }
        }
        if let Some(a) = read_value(&global)
            .unwrap_or_else(|e| {
                errors.push(e);
                None
            })
            .and_then(|g| g.get("oauthAccount").cloned())
        {
            p.email = s(&a, "emailAddress");
            p.organization = s(&a, "organizationName");
            if let Some(plan) = s(&a, "planDisplayName") {
                p.plan = Some(plan);
            }
        }
    }

    fn fill_codex(p: &mut ProfileInfo, dir: &Path, errors: &mut Vec<String>) {
        let Some(auth) = read_value(&dir.join("auth.json")).unwrap_or_else(|e| {
            errors.push(e);
            None
        }) else {
            return;
        };
        let has_key = auth.get("OPENAI_API_KEY").is_some_and(|k| k.as_str().is_some_and(|k| !k.is_empty()));
        let tokens = auth.get("tokens").filter(|t| !t.is_null());
        p.logged_in = has_key || tokens.is_some();
        if let Some(mode) = s(&auth, "auth_mode") {
            let mode = match mode.as_str() {
                "chatgpt" => "Conta ChatGPT".to_string(),
                "apikey" | "api_key" => "Chave de API".to_string(),
                m => m.to_string(),
            };
            p.details.push(Detail { label: "Login".into(), value: mode });
        } else if has_key {
            p.details.push(Detail { label: "Login".into(), value: "Chave de API".into() });
        }
        if let Some(payload) = tokens.and_then(|t| s(t, "id_token")).and_then(|j| jwt_payload(&j)) {
            p.email = s(&payload, "email");
            if let Some(auth) = payload.get("https://api.openai.com/auth") {
                p.plan = s(auth, "chatgpt_plan_type").map(cap);
            }
        }
        if let Some(r) = s(&auth, "last_refresh") {
            p.details.push(Detail { label: "Última renovação".into(), value: r });
        }
    }

    fn fill_agy(p: &mut ProfileInfo, dir: &Path, is_default: bool, errors: &mut Vec<String>) {
        let cli = dir.join(".gemini").join("antigravity-cli");
        let token_file = cli.join("antigravity-oauth-token");
        if is_default {
            // A instalação original guarda o login no Gerenciador de Credenciais.
            p.logged_in = has_windows_credential("gemini:antigravity") || token_file.is_file();
            p.details.push(Detail { label: "Login guardado em".into(), value: "Gerenciador de Credenciais".into() });
        } else {
            p.logged_in = token_file.is_file();
            p.details.push(Detail { label: "Login guardado em".into(), value: "arquivo do perfil".into() });
        }
        // Só lê o campo do e-mail; o token em si não é tocado.
        if let Some(t) = read_value(&token_file).unwrap_or_else(|e| {
            errors.push(e);
            None
        }) {
            p.email = s(&t, "id_token_email");
            if let Some(m) = s(&t, "auth_method") {
                p.details.push(Detail { label: "Método".into(), value: m });
            }
        }
        if p.email.is_none() && p.logged_in {
            p.email = email_in_log(&cli.join("cli.log"));
        }
    }

    pub fn state(&self, env: Option<String>) -> ToolState {
        let env = env.filter(|v| !v.trim().is_empty());
        let mut profiles = vec![self.info(DEFAULT_NAME, &self.default_dir(), env.as_deref())];
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
            profiles.push(self.info(&n, &d, env.as_deref()));
        }
        let env_unknown = self.tool.supports_default() && env.is_some() && !profiles.iter().any(|p| p.is_selected);
        ToolState {
            tool: self.tool,
            label: self.tool.label().into(),
            command: self.tool.command().into(),
            installed: self.tool.installed(),
            supports_default: self.tool.supports_default(),
            env_var: self.tool.env_var().map(String::from),
            profiles_root: self.root.display().to_string(),
            env_value: env,
            env_unknown,
            profiles,
        }
    }

    /// Cria a pasta do perfil e compartilha itens da instalação original.
    /// Retorna avisos não fatais (ex.: link que não pôde ser criado).
    pub fn create(&self, name: &str) -> Result<(String, Vec<String>), String> {
        let n = validate_name(name)?;
        let dir = self.root.join(&n);
        if dir.exists() {
            return Err(format!("O perfil '{n}' de {} já existe.", self.tool.short()));
        }
        fs::create_dir_all(&dir).map_err(|e| format!("Não foi possível criar {}: {e}", dir.display()))?;
        let main = self.default_dir();
        let mut warnings = self.ensure_shared_links(&n);
        for f in self.tool.copied_files() {
            let src = main.join(f);
            if src.is_file() {
                if let Err(e) = fs::copy(&src, dir.join(f)) {
                    warnings.push(format!("não foi possível copiar '{f}': {e}"));
                }
            }
        }
        Ok((n, warnings))
    }

    /// Cria os links compartilhados que faltarem (perfis antigos ganham os novos).
    /// Uma pasta real já existente no perfil não é tocada. Retorna avisos.
    pub fn ensure_shared_links(&self, name: &str) -> Vec<String> {
        if name == DEFAULT_NAME {
            return vec![];
        }
        let dir = self.root.join(name);
        let main = self.default_dir();
        let mut warnings = vec![];
        for d in self.tool.shared_dirs() {
            let src = main.join(d);
            let dst = dir.join(d);
            if fs::symlink_metadata(&dst).is_ok() {
                continue;
            }
            if !src.is_dir() {
                // .ssh ausente não é erro; as pastas de configuração são criadas.
                if d.starts_with('.') {
                    continue;
                }
                if let Err(e) = fs::create_dir_all(&src) {
                    warnings.push(format!("não foi possível criar '{d}': {e}"));
                    continue;
                }
            }
            if let Err(e) = make_dir_link(&src, &dst) {
                warnings.push(format!("não foi possível ligar '{d}': {e}"));
            }
        }
        warnings
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
            format!("Não foi possível renomear (feche os terminais que usam esse perfil): {e}")
        })?;
        Ok(n)
    }

    /// Exclui a pasta do perfil. Links compartilhados são removidos antes,
    /// para nunca apagar o conteúdo da instalação original.
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
            format!("Não foi possível excluir (feche os terminais que usam esse perfil): {e}")
        })
    }
}

fn cap(s: String) -> String {
    let mut c = s.chars();
    match c.next() {
        Some(f) => f.to_uppercase().collect::<String>() + c.as_str(),
        None => s,
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
        let s = Store::new(Tool::Claude, d.path().to_path_buf());
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
        assert_eq!(p.plan.as_deref(), Some("Max"));
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
        // variável com barra final e caixa diferente ainda casa
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

    #[test]
    fn codex_reads_auth_json() {
        use base64::Engine;
        let d = tempfile::tempdir().unwrap();
        let codex = d.path().join(".codex");
        fs::create_dir_all(codex.join("skills")).unwrap();
        let payload = base64::engine::general_purpose::URL_SAFE_NO_PAD.encode(
            r#"{"email":"c@x.com","https://api.openai.com/auth":{"chatgpt_plan_type":"pro"}}"#,
        );
        fs::write(
            codex.join("auth.json"),
            format!(r#"{{"auth_mode":"chatgpt","OPENAI_API_KEY":null,"tokens":{{"id_token":"h.{payload}.s"}},"last_refresh":"2026-01-01"}}"#),
        )
        .unwrap();
        let s = Store::new(Tool::Codex, d.path().to_path_buf());
        let st = s.state(None);
        let p = &st.profiles[0];
        assert!(p.logged_in && p.is_selected);
        assert_eq!(p.email.as_deref(), Some("c@x.com"));
        assert_eq!(p.plan.as_deref(), Some("Pro"));
        let (n, _) = s.create("dev").unwrap();
        assert!(d.path().join(".codex-profiles/dev/skills").exists());
        assert_eq!(s.launch_env(&n).unwrap()[0].0, "CODEX_HOME");
    }

    #[test]
    fn agy_profile_is_fake_home() {
        let d = tempfile::tempdir().unwrap();
        fs::create_dir_all(d.path().join(".ssh")).unwrap();
        fs::write(d.path().join(".gitconfig"), "[user]").unwrap();
        let s = Store::new(Tool::Agy, d.path().to_path_buf());
        let (n, w) = s.create("teste").unwrap();
        assert!(w.is_empty(), "{w:?}");
        let home = d.path().join(".agy-profiles").join("teste");
        assert!(home.join(".ssh").exists() && home.join(".gitconfig").exists());
        let cli = home.join(".gemini/antigravity-cli");
        fs::create_dir_all(&cli).unwrap();
        fs::write(cli.join("antigravity-oauth-token"), r#"{"token":"x","auth_method":"oauth","id_token_email":"g@x.com"}"#).unwrap();
        let st = s.state(None);
        let p = st.profiles.iter().find(|p| p.name == "teste").unwrap();
        assert!(p.logged_in);
        assert_eq!(p.email.as_deref(), Some("g@x.com"));
        let env = s.launch_env(&n).unwrap();
        assert!(env.iter().any(|(k, v)| *k == "SSH_CONNECTION" && v.is_some()));
        assert!(env.iter().any(|(k, v)| *k == "USERPROFILE" && v.as_deref() == Some(home.to_str().unwrap())));
        assert!(s.env_for(&n).is_err(), "agy não tem padrão do sistema");
        s.delete("teste").unwrap();
        assert!(d.path().join(".ssh").exists(), ".ssh original intacta");
    }
}

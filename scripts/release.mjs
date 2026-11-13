#!/usr/bin/env node
// Publica uma release: sobe a versão, compila assinado, gera latest.json,
// cria a release no repositório público e envia commit + tag.
//
//   npm run release -- 3.2.0 "Notas da versão"
//
// Requisitos: gh autenticado com acesso à UrubuCode e a chave do updater em
// ~/.tauri/claude-profile-manager.key (ou TAURI_SIGNING_PRIVATE_KEY definida).

import { execFileSync } from "node:child_process";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";

const RELEASES_REPO = "UrubuCode/claude-profile-manager-releases";
const root = path.resolve(path.dirname(new URL(import.meta.url).pathname.replace(/^\/(\w:)/, "$1")), "..");
const [version, notes = "Melhorias e correções."] = process.argv.slice(2);

const die = (m) => { console.error(`\n✖ ${m}`); process.exit(1); };
// No Windows, npm/npx são .cmd e precisam de shell; o resto roda direto (argumentos
// com espaço, como notas e mensagem de commit, chegam intactos).
const needsShell = (cmd) => process.platform === "win32" && (cmd === "npm" || cmd === "npx");
const run = (cmd, args, opts = {}) =>
  execFileSync(cmd, args, { cwd: root, stdio: "inherit", shell: needsShell(cmd), ...opts });
const out = (cmd, args) => execFileSync(cmd, args, { cwd: root, encoding: "utf8", shell: needsShell(cmd) }).trim();

if (!/^\d+\.\d+\.\d+$/.test(version ?? "")) die('Uso: npm run release -- <x.y.z> "notas"');
const tag = `v${version}`;

// ---- checagens ----
if (out("git", ["status", "--porcelain"])) die("Há mudanças não commitadas. Faça commit ou stash antes.");
if (out("git", ["tag", "-l", tag])) die(`A tag ${tag} já existe.`);
out("gh", ["auth", "status"]);

if (!process.env.TAURI_SIGNING_PRIVATE_KEY) {
  const keyFile = path.join(os.homedir(), ".tauri", "claude-profile-manager.key");
  if (!fs.existsSync(keyFile)) die(`Chave do updater não encontrada em ${keyFile}`);
  process.env.TAURI_SIGNING_PRIVATE_KEY = fs.readFileSync(keyFile, "utf8").trim();
}
process.env.TAURI_SIGNING_PRIVATE_KEY_PASSWORD ??= "";

// ---- versão ----
const bump = (file, re, rep) => {
  const p = path.join(root, file);
  const s = fs.readFileSync(p, "utf8");
  if (!re.test(s)) die(`Versão não encontrada em ${file}`);
  fs.writeFileSync(p, s.replace(re, rep));
};
bump("package.json", /"version": "[^"]+"/, `"version": "${version}"`);
bump("src-tauri/tauri.conf.json", /"version": "[^"]+"/, `"version": "${version}"`);
bump("src-tauri/Cargo.toml", /^version = "[^"]+"/m, `version = "${version}"`);
run("npm", ["install", "--package-lock-only", "--no-audit", "--no-fund"]);

// ---- testes + build assinado ----
run("cargo", ["test", "--quiet"], { cwd: path.join(root, "src-tauri") });
run("npx", ["tauri", "build"]);

// ---- artefatos com nomes sem espaço ----
const bundle = path.join(root, "src-tauri", "target", "release", "bundle");
const stage = fs.mkdtempSync(path.join(os.tmpdir(), `cpm-${version}-`));
const files = {
  nsis: [`nsis/Claude Profile Manager_${version}_x64-setup.exe`, `Claude.Profile.Manager_${version}_x64-setup.exe`],
  msi: [`msi/Claude Profile Manager_${version}_x64_en-US.msi`, `Claude.Profile.Manager_${version}_x64_en-US.msi`],
};
const base = `https://github.com/${RELEASES_REPO}/releases/download/${tag}`;
const platform = {};
for (const [kind, [src, dst]] of Object.entries(files)) {
  fs.copyFileSync(path.join(bundle, src), path.join(stage, dst));
  fs.copyFileSync(path.join(bundle, `${src}.sig`), path.join(stage, `${dst}.sig`));
  platform[kind] = { signature: fs.readFileSync(path.join(stage, `${dst}.sig`), "utf8").trim(), url: `${base}/${dst}` };
}
fs.writeFileSync(path.join(stage, "latest.json"), JSON.stringify({
  version, notes, pub_date: new Date().toISOString(),
  platforms: {
    "windows-x86_64": platform.nsis,
    "windows-x86_64-nsis": platform.nsis,
    "windows-x86_64-msi": platform.msi,
  },
}, null, 2));

// ---- commit, tag, push ----
run("git", ["add", "package.json", "package-lock.json", "src-tauri/tauri.conf.json", "src-tauri/Cargo.toml", "src-tauri/Cargo.lock"]);
run("git", ["commit", "-m", `Release ${tag}`]);
run("git", ["tag", "-a", tag, "-m", `Claude Profile Manager ${tag}`]);
run("git", ["push", "origin", "HEAD", tag]);

// ---- release pública ----
const body = `${notes}\n\nInstale com o \`*-setup.exe\` (NSIS) ou o \`.msi\`. Para ativar o menu "Abrir Claude aqui" no Explorer, marque "Menu no Explorer" no app.`;
run("gh", ["release", "create", tag, "-R", RELEASES_REPO, "--title", `Claude Profile Manager ${tag}`,
  "--notes", body, ...fs.readdirSync(stage).map((f) => path.join(stage, f))]);

console.log(`\n✔ Publicado: https://github.com/${RELEASES_REPO}/releases/tag/${tag}`);

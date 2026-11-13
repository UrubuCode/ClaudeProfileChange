; Migração do "Claude Profile Manager" (nome antigo): o novo nome muda a pasta
; de instalação, então o app antigo é desinstalado em silêncio antes, para não
; ficarem os dois. Os perfis (~/.claude-profiles etc.) não são tocados.
!macro NSIS_HOOK_PREINSTALL
  ReadRegStr $R0 HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\Claude Profile Manager" "InstallLocation"
  StrCpy $R1 $R0 1
  ${If} $R1 == '"'
    StrCpy $R0 $R0 "" 1
    StrCpy $R0 $R0 -1
  ${EndIf}
  ${If} $R0 == ""
    StrCpy $R0 "$LOCALAPPDATA\Claude Profile Manager"
  ${EndIf}
  ${If} ${FileExists} "$R0\uninstall.exe"
    DetailPrint "Removendo a versão antiga (Claude Profile Manager)..."
    ExecWait '"$R0\uninstall.exe" /S _?=$R0'
    Delete "$R0\uninstall.exe"
    RMDir "$R0"
  ${EndIf}
!macroend

; Instala o menu "Abrir IA aqui" do Explorer junto com o app
; (também roda em atualizações, mantendo o caminho do executável certo).
!macro NSIS_HOOK_POSTINSTALL
  ExecWait '"$INSTDIR\${MAINBINARYNAME}.exe" --menu on'
!macroend

; Remove o menu ao desinstalar.
; (Atualizações instalam por cima e não passam pela desinstalação.)
!macro NSIS_HOOK_PREUNINSTALL
  ExecWait '"$INSTDIR\${MAINBINARYNAME}.exe" --menu off'
!macroend

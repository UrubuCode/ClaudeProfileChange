; Instala o menu "Abrir Claude aqui" do Explorer junto com o app
; (também roda em atualizações, mantendo o caminho do executável certo).
!macro NSIS_HOOK_POSTINSTALL
  ExecWait '"$INSTDIR\${MAINBINARYNAME}.exe" --menu on'
!macroend

; Remove o menu ao desinstalar.
; (Atualizações instalam por cima e não passam pela desinstalação.)
!macro NSIS_HOOK_PREUNINSTALL
  ExecWait '"$INSTDIR\${MAINBINARYNAME}.exe" --menu off'
!macroend

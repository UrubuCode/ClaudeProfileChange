; Remove o menu "Abrir Claude aqui" do Explorer ao desinstalar.
; (Atualizações instalam por cima e não passam pela desinstalação.)
!macro NSIS_HOOK_PREUNINSTALL
  ExecWait '"$INSTDIR\${MAINBINARYNAME}.exe" --menu off'
!macroend

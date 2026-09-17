#!/bin/zsh
# Duplo clique no Finder. A pasta do atalho é a pasta servida.
APP_DIR=${0:A:h}
cd -- "$APP_DIR" || exit 1
if ! command -v python3 >/dev/null 2>&1; then
  print 'Python 3 não foi encontrado. O JP Wealth não foi iniciado.'
  read '?Pressione Enter para fechar.'
  exit 1
fi
if ! python3 "$APP_DIR/tools/launch_local.py" "$@"; then
  if [[ -t 0 ]]; then read '?Pressione Enter para fechar.'; fi
  exit 1
fi

#!/bin/bash

# Script para mostrar estrutura de pastas e arquivos no terminal
# Ignora diretórios comuns que poluem a visualização

if command -v tree &> /dev/null
then
    tree -a -I ".git|node_modules|venv|__pycache__|.pytest_cache"
else
    find . \( -path "./.git" -o -path "./venv" -o -path "./node_modules" -o -name "__pycache__" -o -name ".pytest_cache" \) -prune -o -print | sed -e 's;[^/]*/;|__;g;s;__|;  |;g'
fi

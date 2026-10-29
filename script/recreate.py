#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Recrée une arborescence à partir d'une sortie `tree` (avec correction
des caractères mangled par un mauvais décodage d'encodage).

Usage :
    python3 recreate_tree.py tree.txt [dossier_base]
"""

import os
import re
import sys


def fix_line(line: str) -> str:
    """Corrige les caractères de dessin mangled par CP1251."""
    # Séquences composées (faire AVANT les remplacements simples)
    line = line.replace('в”њв”Ђв”Ђ', '├──')
    line = line.replace('в””в”Ђв”Ђ', '└──')
    # Caractères simples
    line = line.replace('в”‚', '│')
    line = line.replace('в”Ђ', '─')
    # Espaces insécables déguisés en "В" (V cyrillique)
    line = line.replace('В ', ' ')
    line = line.replace('В', ' ')
    line = line.replace('\xa0', ' ')
    return line


def parse_tree(content: str):
    """Retourne (nom_racine, [(depth, nom), ...])."""
    entries = []
    root_name = None

    for raw in content.split('\n'):
        raw = raw.rstrip('\r\n')
        if not raw.strip():
            continue

        line = fix_line(raw)
        if not line.strip():
            continue

        # Ligne racine (pas de connecteurs ├/└/│)
        if '├' not in line and '└' not in line and '│' not in line:
            if root_name is None:
                root_name = line.strip()
            continue

        # Ligne d'élément : (prefix 4-chars)* + ├──/└── + ' ' + nom
        m = re.match(r'^((?:[│ ]{4})*)[├└]── (.*)$', line)
        if not m:
            continue

        prefix, name = m.groups()
        name = name.strip()
        if not name:
            continue

        depth = len(prefix) // 4
        entries.append((depth, name))

    return root_name, entries


def is_file_by_ext(name: str) -> bool:
    """Heuristique : présence d'une extension => fichier."""
    return bool(os.path.splitext(name)[1])


def create_structure(entries, base_dir):
    """Crée dossiers et fichiers selon les entrées (depth, name)."""
    path_stack = {}
    n_dirs = n_files = 0

    for idx, (depth, name) in enumerate(entries):
        # Détection du type via look-ahead
        is_dir = None
        if idx + 1 < len(entries) and entries[idx + 1][0] > depth:
            is_dir = True
        if is_dir is None:
            is_dir = not is_file_by_ext(name) and False  # défaut : fichier
            # Si pas d'extension ET on est en fin de sous-arbre,
            # on garde "fichier" pour ne rien casser (les dossiers
            # vides restent rares dans une vraie sortie tree).

        parent = path_stack.get(depth - 1, base_dir) if depth else base_dir
        path = os.path.join(parent, name)
        path_stack[depth] = path

        if is_dir:
            try:
                os.makedirs(path, exist_ok=True)
                n_dirs += 1
            except OSError as e:
                print(f"[warn] dossier {path}: {e}")
        else:
            parent_dir = os.path.dirname(path)
            if parent_dir:
                os.makedirs(parent_dir, exist_ok=True)
            if not os.path.exists(path):
                try:
                    open(path, 'w').close()
                    n_files += 1
                except OSError as e:
                    print(f"[warn] fichier {path}: {e}")

    print(f"→ {n_dirs} dossiers, {n_files} fichiers créés")


def main():
    if len(sys.argv) < 2:
        print("Usage : python3 recreate_tree.py <tree.txt> [base_dir]")
        sys.exit(1)

    tree_file = sys.argv[1]
    base_dir = sys.argv[2] if len(sys.argv) > 2 else '.'

    with open(tree_file, 'r', encoding='utf-8', errors='replace') as f:
        content = f.read()

    root_name, entries = parse_tree(content)
    print(f"Racine   : {root_name!r}")
    print(f"Entrées  : {len(entries)}")

    # Création du dossier racine si ce n'est pas '.' ou '..'
    if root_name and root_name not in ('.', '..'):
        base_dir = os.path.join(base_dir, root_name)
        os.makedirs(base_dir, exist_ok=True)

    create_structure(entries, base_dir)
    print(f"Terminé dans : {os.path.abspath(base_dir)}")


if __name__ == '__main__':
    main()
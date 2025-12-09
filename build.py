#!/usr/bin/env python3
"""
Build script for Claude Profile Manager

Creates a standalone executable using PyInstaller.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path


def check_pyinstaller():
    """Check if PyInstaller is installed, install if needed."""
    try:
        import PyInstaller
        print("[OK] PyInstaller já está instalado")
        return True
    except ImportError:
        print("[INFO] Instalando PyInstaller...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
            print("[OK] PyInstaller instalado com sucesso")
            return True
        except subprocess.CalledProcessError:
            print("[ERROR] Erro ao instalar PyInstaller")
            return False


def clean_build_dirs():
    """Clean previous build directories."""
    dirs_to_clean = ["build", "dist", "__pycache__"]

    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            print(f"[CLEAN] Limpando diretório: {dir_name}")
            shutil.rmtree(dir_name)


def create_spec_file():
    """Create PyInstaller spec file for better control."""
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[
        'tkinter',
        'tkinter.ttk',
        'tkinter.messagebox',
        'tkinter.simpledialog',
        'tkinter.filedialog',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'numpy',
        'pandas',
        'scipy',
        'PIL',
        'cv2',
        'tensorflow',
        'torch',
        'jupyter',
        'notebook',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='ClaudeProfileManager',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # No console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # Add icon file here if available
)
'''

    with open("ClaudeProfileManager.spec", "w", encoding="utf-8") as f:
        f.write(spec_content)

    print("[INFO] Arquivo .spec criado")


def build_executable():
    """Build the executable using PyInstaller."""
    print("[BUILD] Construindo executável...")

    try:
        # Use the spec file for better control
        cmd = [
            sys.executable, "-m", "PyInstaller",
            "--clean",
            "--noconfirm",
            "ClaudeProfileManager.spec"
        ]

        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("[OK] Build concluído com sucesso!")
        return True

    except subprocess.CalledProcessError as e:
        print("[ERROR] Erro durante o build:")
        print(f"Return code: {e.returncode}")
        print(f"STDOUT: {e.stdout}")
        print(f"STDERR: {e.stderr}")
        return False


def organize_output():
    """Organize the output files."""
    dist_dir = Path("dist")
    if not dist_dir.exists():
        print("[ERROR] Diretório dist não encontrado")
        return

    # Create release directory
    release_dir = Path("release")
    release_dir.mkdir(exist_ok=True)

    # Copy executable
    exe_file = dist_dir / "ClaudeProfileManager.exe"
    if exe_file.exists():
        shutil.copy2(exe_file, release_dir / "ClaudeProfileManager.exe")
        print(f"[COPY] Executável copiado para: {release_dir / 'ClaudeProfileManager.exe'}")

        # Copy README
        readme_file = Path("README.md")
        if readme_file.exists():
            shutil.copy2(readme_file, release_dir / "README.md")

        print(f"[OK] Release preparado em: {release_dir.absolute()}")
        print(f"[INFO] Tamanho do executável: {exe_file.stat().st_size / 1024 / 1024:.1f} MB")
    else:
        print("[ERROR] Executável não encontrado")


def main():
    """Main build process."""
    print("Claude Profile Manager - Build Script")
    print("=" * 50)

    # Check Python version
    if sys.version_info < (3, 8):
        print("[ERROR] Python 3.8+ é necessário")
        return False

    print(f"[INFO] Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")

    # Check and install PyInstaller
    if not check_pyinstaller():
        return False

    # Clean previous builds
    clean_build_dirs()

    # Create spec file
    create_spec_file()

    # Build executable
    if build_executable():
        organize_output()
        print("\n[OK] Build concluído com sucesso!")
        print("[INFO] Execute: release/ClaudeProfileManager.exe")
        return True
    else:
        print("\n[ERROR] Build falhou")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
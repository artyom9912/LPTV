# -*- mode: python ; coding: utf-8 -*-
from kivy_deps import sdl2, glew
block_cipher = None


a = Analysis(['C:\\Users\\ekosh\\PycharmProjects\\LPTV\\MainForm.py'],
             pathex=['C:\\Users\\ekosh\\Desktop\\artemkens\\LPTV'],
             binaries=[],
             datas=[],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='LPTV',
          debug=True,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=True , icon='C:\\Users\\ekosh\\Desktop\\artemkens\\LPTV\\icon.ico')
coll = COLLECT(exe, Tree('C:\\Users\\ekosh\\PycharmProjects\\LPTV'),
               a.binaries,
               a.zipfiles,
               a.datas,
               *[Tree(p) for p in (sdl2.dep_bins + glew.dep_bins)],
               strip=False,
               upx=True,
               upx_exclude=[],
               name='M')

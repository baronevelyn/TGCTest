# Build Windows .exe (No Python required)

This guide builds a standalone `MiniTCG.exe` using PyInstaller so players can run the game without installing Python or dependencies.

## Prerequisites
- Windows 10/11
- PowerShell
- Python 3.11 installed on the build machine (only for building)

## Quick Build
```powershell
# From repo root
./build_exe.ps1 -Windowed -Clean
# Output: dist/MiniTCG/MiniTCG.exe
```

- `-Windowed`: builds without console window (default). Omit to show console.
- `-Clean`: removes previous `build/` and `dist/` before building.

## What’s included
- All Python code bundled
- Required dependencies (`requirements.txt`)
- Folders copied into the build:
  - `assets/` (images, icons)
  - `data/` (optional logs/config)
  - `docs/` (optional)
- Optional icon if `assets/app.ico` exists
- `server_config.txt` is copied into the `dist/MiniTCG` folder so you can change server URL without rebuilding

## Distribute to friends
- Send the entire folder `dist/MiniTCG/`
- They launch `MiniTCG.exe`
- No Python or pip needed

## Troubleshooting
- If images don’t appear, ensure `assets/` is included and paths in code use relative paths.
- If antivirus flags the exe, sign it or zip the folder and share.
- If the exe crashes on start, run a console build to see logs:
```powershell
./build_exe.ps1 -Windowed:$false -Clean
```

## Advanced (manual command)
If you prefer running PyInstaller directly:
```powershell
python -m pip install pyinstaller
python -m PyInstaller --name MiniTCG --noconsole --clean --noconfirm \
  --add-data assets;assets \
  --add-data data;data \
  --add-data docs;docs \
  main_menu.py
```

## Notes
- This builds the client game (`main_menu.py`). The online server on Render is separate and does not need to be included.
- If you add new asset folders, update `build_exe.ps1` `assets` array.

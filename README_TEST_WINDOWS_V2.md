# VEO_GROK V2.3.2 Option3 Patch v2

This is v2 Windows-test build. It fixes the previous PyInstaller decompression error by preserving the original PYZ/EXE size and archive layout, replacing only the compressed `license_server_client` entry with padding.

## Use
1. Extract this ZIP fully.
2. Run `Auto_Veo3_Grok_HieuMMO_V2.3.2_option3_patch_v2.exe`.
3. Use the UI normally.
4. If the old error `Invalid token signature` was caused by stale/corrupt volatile license session/permit cache, the app will clear volatile cache and retry verify/run-permit once.

## Safety
No credentials/tokens are included. License validators/server verify/run-permit remain required.

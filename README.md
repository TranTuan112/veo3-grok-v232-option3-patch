# VEO_GROK V2.3.2 option3 Windows-test build

Artifact: `Auto_Veo3_Grok_HieuMMO_V2.3.2_option3_patch.exe`

Patch behavior: keeps license server verification, session token validation, run-permit request, and permit payload validation required. It changes only volatile cache retry behavior in `license_server_client.ensure_run_permit`: on recoverable token/signature/expiry/mismatch/session/permit validation errors, it clears cached permit for the stage and cached server session/signature/checked_at, then retries run-permit once. It fails closed if validators or server permit still fail.

This EXE is a Linux-built/static-verified Windows-test artifact; runtime execution must be tested on Windows.

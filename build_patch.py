import marshal, struct, zlib, types, hashlib
from pathlib import Path
SRC_EXE=Path('/tmp/veo3_grok_v232_newjob/Auto_Veo3_Grok_HieuMMO_V2.3.2.exe'); SRC_PYZ=Path('/tmp/veo3_grok_v232_newjob/Auto_Veo3_Grok_HieuMMO_V2.3.2.exe_extracted/PYZ.pyz')
OUT=Path('/tmp/veo3_grok_v232_release'); OUT.mkdir(exist_ok=True)
PATCHED_PYZ=OUT/'PYZ_option3_patch.pyz'; PATCHED_EXE=OUT/'Auto_Veo3_Grok_HieuMMO_V2.3.2_option3_patch.exe'; MARK='OPTION3_PATCH_RETRY_VOLATILE_LICENSE_CACHE_V232'
def sha(p):
 h=hashlib.sha256(); h.update(Path(p).read_bytes()); return h.hexdigest()
def repl_const(c,new):
 const=list(c.co_consts)
 for i,x in enumerate(const):
  if isinstance(x,types.CodeType) and x.co_name=='ensure_run_permit': const[i]=new; return c.replace(co_consts=tuple(const))
 raise KeyError('ensure_run_permit')
pyz=SRC_PYZ.read_bytes(); tocpos=struct.unpack('!i',pyz[8:12])[0]; toc=marshal.loads(pyz[tocpos:])
idx=next(i for i,(n,e) in enumerate(toc) if n=='license_server_client'); n,(typ,pos,ln)=toc[idx]
orig_code=marshal.loads(zlib.decompress(pyz[pos:pos+ln]))
patch_src=f'''
def ensure_run_permit(stage="workflow", metadata=None, logger=None):
    _option3_patch_marker = "{MARK}"
    stage_key = str(stage or "workflow").strip() or "workflow"
    for _option3_attempt in (0, 1):
        try:
            cached = _PERMIT_CACHE.get(stage_key)
            if cached and cached.get("permit") and int(cached.get("expiresAt") or 0) > int(time.time()) + 10:
                return cached
            state = ensure_fresh_license_session(app_version=_current_app_version(), logger=logger)
            session = (((state or {{}}).get("server") or {{}}).get("session") or {{}})
            token = str(session.get("token") or "")
            if not token: raise LicenseServerError("License server session token is missing")
            session_payload = _validate_session_token(str(token), expected_machine_id=make_machine_id(), expected_app_version=_current_app_version(), expected_expires_at=int(session.get("expiresAt") or 0))
            payload = {{"sessionToken": token, "machineId": make_machine_id(), "stage": stage_key, "nonce": uuid.uuid4().hex, "timestamp": int(time.time()), "metadata": metadata or {{}}}}
            status, data, _ = _post_json("/api/license/run-permit", payload, timeout=15)
            if status >= 400 or not data.get("ok") or not data.get("allowed"): raise LicenseServerError(str(data.get("error") or "License server did not allow this run"))
            validated = _validate_permit_payload(stage_key, data, make_machine_id(), expected_key_hash=str(session_payload.get("keyHash") or ""))
            _PERMIT_CACHE[stage_key] = validated
            if logger:
                try: logger(f"🔐 License server permit OK | stage={{stage_key}}")
                except Exception: pass
            return validated
        except LicenseServerError as exc:
            if _option3_attempt or not any(m in str(exc).lower() for m in ("token","signature","expired","expire","mismatch","machine","appversion","keyhash","session","permit")): raise
            try: _PERMIT_CACHE.pop(stage_key, None)
            except Exception: pass
            try:
                state = _load_state(); server = state.get("server") if isinstance(state, dict) else None
                if isinstance(server, dict):
                    server.pop("session", None); server.pop("signature", None); server.pop("checked_at", None)
                    _save_state(state)
            except Exception: pass
            if logger:
                try: logger(f"🔐 License server: refreshed cached session/permit after validation error | stage={{stage_key}}")
                except Exception: pass
'''
ns={}; exec(compile(patch_src,'license_server_client.py','exec'),ns)
new_code=repl_const(orig_code, ns['ensure_run_permit'].__code__); new_blob=zlib.compress(marshal.dumps(new_code),9)
# allow shifting following entries and TOC; update offset/length. No validators changed.
new_pyz = bytearray(); new_pyz += pyz[:pos]; new_pyz += new_blob; new_pyz += pyz[pos+ln:tocpos]
delta=len(new_blob)-ln
new_toc=[]
for name,(t,p,l) in toc:
 if name=='license_server_client': new_toc.append((name,(t,p,len(new_blob))))
 elif p>pos: new_toc.append((name,(t,p+delta,l)))
 else: new_toc.append((name,(t,p,l)))
new_tocpos=tocpos+delta; new_pyz += marshal.dumps(new_toc); new_pyz[8:12]=struct.pack('!i',new_tocpos)
PATCHED_PYZ.write_bytes(new_pyz)
exe=SRC_EXE.read_bytes();
if exe.count(pyz)!=1: raise SystemExit('original PYZ not unique in EXE')
PATCHED_EXE.write_bytes(exe.replace(pyz, bytes(new_pyz),1))
print('orig_exe_sha256='+sha(SRC_EXE)); print('patched_exe_sha256='+sha(PATCHED_EXE)); print('patched_pyz_sha256='+sha(PATCHED_PYZ)); print('orig_pyz_size',len(pyz),'patched_pyz_size',len(new_pyz),'delta',delta,'marker='+MARK)

import marshal,struct,zlib,types,hashlib
from pathlib import Path
pyz=Path('/tmp/veo3_grok_v232_release/PYZ_option3_patch.pyz').read_bytes()
off=struct.unpack('!i',pyz[8:12])[0]; toc=marshal.loads(pyz[off:])
for n,(t,p,l) in toc:
 if n=='license_server_client': code=marshal.loads(zlib.decompress(pyz[p:p+l])); break
else: raise SystemExit('missing')
found=False
for x in code.co_consts:
 if isinstance(x,types.CodeType) and x.co_name=='ensure_run_permit':
  s=str(x.co_consts); found='OPTION3_PATCH_RETRY_VOLATILE_LICENSE_CACHE_V232' in s and '_validate_session_token' in x.co_names and '_validate_permit_payload' in x.co_names and '_post_json' in x.co_names
  print('ensure_names=',x.co_names); print('marker_found=', 'OPTION3_PATCH_RETRY_VOLATILE_LICENSE_CACHE_V232' in s); print('validators_present=', found)
print('VERIFY_OK' if found else 'VERIFY_FAIL')

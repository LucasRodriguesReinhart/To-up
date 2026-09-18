import socket,json,pathlib,sys
code=pathlib.Path(sys.argv[1]).read_text(encoding='utf-8')
s=socket.create_connection(('127.0.0.1',9876),timeout=10); s.settimeout(180)
s.sendall(json.dumps({'type':'execute_code','params':{'code':code}}).encode())
b=b''
while True:
    c=s.recv(65536)
    if not c: break
    b+=c
    try:
        obj=json.loads(b); print(json.dumps(obj,ensure_ascii=False)); break
    except json.JSONDecodeError: pass
s.close()

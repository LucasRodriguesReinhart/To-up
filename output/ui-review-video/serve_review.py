from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import re

ROOT=Path(__file__).resolve().parent
class Handler(SimpleHTTPRequestHandler):
    def __init__(self,*args,**kwargs):super().__init__(*args,directory=str(ROOT),**kwargs)
    def send_head(self):
        self.remaining=None
        path=Path(self.translate_path(self.path))
        if path.suffix.lower()=='.mp4' and path.is_file():
            size=path.stat().st_size
            header=self.headers.get('Range')
            start,end=0,size-1
            if header:
                m=re.fullmatch(r'bytes=(\d*)-(\d*)',header)
                if not m or not any(m.groups()):
                    self.send_error(416);return None
                a,b=m.groups()
                if a:start=int(a);end=min(int(b),size-1) if b else size-1
                else:start=max(0,size-int(b))
                if start>=size or start>end:
                    self.send_response(416);self.send_header('Content-Range',f'bytes */{size}');self.end_headers();return None
            self.send_response(206 if header else 200)
            self.send_header('Content-Type','video/mp4')
            self.send_header('Accept-Ranges','bytes')
            self.send_header('Content-Length',str(end-start+1))
            if header:self.send_header('Content-Range',f'bytes {start}-{end}/{size}')
            self.end_headers();f=path.open('rb');f.seek(start);self.remaining=end-start+1;return f
        return super().send_head()
    def copyfile(self,source,output):
        try:
            if self.remaining is None:return super().copyfile(source,output)
            while self.remaining>0:
                chunk=source.read(min(1024*256,self.remaining))
                if not chunk:break
                output.write(chunk);self.remaining-=len(chunk)
        except (BrokenPipeError,ConnectionResetError,ConnectionAbortedError):pass

if __name__=='__main__':
    print('Questionário: http://127.0.0.1:8766/Questionario-UI.html',flush=True)
    ThreadingHTTPServer(('127.0.0.1',8766),Handler).serve_forever()

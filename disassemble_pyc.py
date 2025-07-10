import dis
import marshal

with open(r'C:\Users\Roma\Desktop\doc\ffmpeg_utils.cpython-313.pyc', 'rb') as f:
    f.read(16)  # Пропускаем заголовок .pyc
    code = marshal.load(f)
    dis.dis(code) 
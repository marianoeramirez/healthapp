#!/usr/bin/env python3
from pathlib import Path
import secrets

p = Path('.env')
text = p.read_text().replace('\r\n', '\n').replace('\r', '\n')
lines = []
for line in text.splitlines():
    if line.startswith('SECRET_KEY=') and (
        'change-me' in line or 'dev-placeholder' in line or len(line) < 40
    ):
        lines.append('SECRET_KEY=' + secrets.token_urlsafe(50))
    else:
        lines.append(line)
p.write_text('\n'.join(lines) + '\n')
print('env normalized')
for line in p.read_text().splitlines():
    if line.startswith('SECRET_KEY='):
        print('SECRET_KEY=***')
    else:
        print(line)

#!/usr/bin/env python3
"""Merge PostgreSQL settings into .env; leave POSTGRES_PASSWORD for manual input."""
from pathlib import Path

ENV_PATH = Path('.env')

desired = {
    'POSTGRES_HOST': '35.193.62.211',
    'POSTGRES_PORT': '5432',
    'POSTGRES_DB': 'healthapp',
    'POSTGRES_USER': 'healthapp',
    'POSTGRES_PASSWORD': '',
}

text = ENV_PATH.read_text().replace('\r\n', '\n').replace('\r', '\n') if ENV_PATH.exists() else ''
values = {}
order = []
for line in text.splitlines():
    if not line or line.startswith('#') or '=' not in line:
        continue
    key, _, value = line.partition('=')
    values[key] = value
    order.append(key)

# Drop sqlite-only path when using Postgres
values.pop('DATABASE_PATH', None)
if 'DATABASE_PATH' in order:
    order = [k for k in order if k != 'DATABASE_PATH']

for key, value in desired.items():
    if key == 'POSTGRES_PASSWORD' and values.get('POSTGRES_PASSWORD'):
        # Keep an existing password if already set
        continue
    values[key] = value
    if key not in order:
        order.append(key)

lines = [f'{key}={values[key]}' for key in order]
ENV_PATH.write_text('\n'.join(lines) + '\n')
print('Updated .env PostgreSQL settings (password left empty unless already set).')
for key in order:
    if key == 'POSTGRES_PASSWORD':
        print('POSTGRES_PASSWORD=' + ('***' if values[key] else '(empty — set this)'))
    elif key == 'SECRET_KEY':
        print('SECRET_KEY=***')
    else:
        print(f'{key}={values[key]}')

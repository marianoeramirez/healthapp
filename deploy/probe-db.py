#!/usr/bin/env python3
import socket

for port in (5432, 3306):
    try:
        s = socket.create_connection(('35.193.62.211', port), 3)
        s.close()
        print(f'{port} open')
    except Exception as e:
        print(f'{port} closed: {e}')

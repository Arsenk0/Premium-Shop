import os
import re

def process_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    def rpl(m):
        return ' '.join(m.group(0).split())

    new_content = re.sub(r'\{%[\s\n]*trans[\s\n]+"[^"]*"[\s\n]*%\}', rpl, content)
    new_content = re.sub(r'\{%[\s\n]*trans[\s\n]+' + r"'[^']*'" + r'[\s\n]*%\}', rpl, new_content)

    if content != new_content:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print("Fixed", path)

for root, _, files in os.walk('templates'):
    for f in files:
        if f.endswith('.html'):
            process_file(os.path.join(root, f))

import os
import re

count = 0
for root, _, files in os.walk('templates'):
    for f in files:
        if f.endswith('.html'):
            path = os.path.join(root, f)
            with open(path, 'r', encoding='utf-8') as file:
                content = file.read()
            
            def rpl(m):
                global count
                count += 1
                return ' '.join(m.group(0).split())
            
            # Match {% trans "..." %} or {% trans '...' %}
            new_content = re.sub(r'\{%[\s\n]*trans[\s\n]+"[^"]*"[\s\n]*%\}', rpl, content)
            new_content = re.sub(r"\{%[\s\n]*trans[\s\n]+'[^']*'[\s\n]*%\}", rpl, new_content)
            
            # Match {{ variable.name }}
            new_content = re.sub(r'\{\{[\s\n]*[a-zA-Z0-9_\.]+[\s\n]*\}\}', rpl, new_content)

            if content != new_content:
                with open(path, 'w', encoding='utf-8') as file:
                    file.write(new_content)
                print("Fixed", path)

print("Total fixes:", count)

import os
import re

count_trans = 0
count_vars = 0

for root, _, files in os.walk('templates'):
    for f in files:
        if f.endswith('.html'):
            path = os.path.join(root, f)
            with open(path, 'r', encoding='utf-8') as file:
                content = file.read()
            
            original_content = str(content)
            
            def fix_trans(m):
                global count_trans
                count_trans += 1
                return ' '.join(m.group(0).split())
                
            def fix_vars(m):
                global count_vars
                count_vars += 1
                return ' '.join(m.group(0).split())

            # Find broken {% trans ... %} spanning multiple lines
            # A valid trans tag could be spanning linebreaks because a formatter broke it
            new_content = re.sub(r'\{%\s*trans\s+"[^"]*"\s*%\}', fix_trans, content)
            new_content = re.sub(r"\{%\s*trans\s+'[^']*'\s*%\}", fix_trans, new_content)
            
            # Find broken {{ variable }} spanning multiple lines
            new_content = re.sub(r'\{\{\s*[a-zA-Z0-9_\.]+\s*\}\}', fix_vars, new_content)

            if original_content != new_content:
                with open(path, 'w', encoding='utf-8') as file:
                    file.write(new_content)
                print("FIXED FILE:", path)

print("Total trans fixes:", count_trans)
print("Total var fixes:", count_vars)

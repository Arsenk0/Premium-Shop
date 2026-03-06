import os
import re

def fix_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Regex to find {% trans ... %} that might span across newlines
    # We want to replace newlines inside the tag with spaces
    def replacer(match):
        # replace newlines and excessive spaces with a single space
        return re.sub(r'\s+', ' ', match.group(0))

    new_content = re.sub(r'\{%\s*trans[^%]+%\}', replacer, content, flags=re.MULTILINE)
    
    # Also fix {% blocktrans %}...{% endblocktrans %} and other tags if they got broken in a similar way, 
    # but let's stick to {% trans ... %} for now as it's the most common.
    
    if new_content != content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Fixed {filepath}")

for root, dirs, files in os.walk('templates'):
    for file in files:
        if file.endswith('.html'):
            fix_file(os.path.join(root, file))

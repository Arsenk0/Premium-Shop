import os
import re

count = 0
for root, _, files in os.walk('templates'):
    for f in files:
        if f.endswith('.html'):
            path = os.path.join(root, f)
            with open(path, 'r', encoding='utf-8') as file:
                content = file.read()
            
            # Find {% trans \n "text" %} and similar forms
            def rpl(m):
                global count
                count += 1
                # Replace all whitespace within the matched tag with a single space
                # But to preserve the string itself, let's just do a simple replace:
                s = m.group(0)
                # s is like {% trans \n "Text" %}
                # We want {% trans "Text" %}
                s = re.sub(r'\s+', ' ', s)
                # Ensure no spaces inside the curly braces boundaries
                s = s.replace('{% ', '{%').replace(' %}', '%}')
                # ensure there's a space after trans
                s = s.replace('{%trans', '{% trans').replace('trans"', 'trans "').replace("trans'", "trans '")
                # Put space before and after
                s = s.replace('{%', '{% ').replace('%}', ' %}')
                # Now collapse internal multiple spaces
                s = re.sub(r'\s+', ' ', s)
                return s
            
            new_content = re.sub(r'\{%\s*trans\s+"[^"]*"\s*%\}', rpl, content)
            new_content = re.sub(r"\{%\s*trans\s+'[^']*'\s*%\}", rpl, new_content)

            if content != new_content:
                with open(path, 'w', encoding='utf-8') as file:
                    file.write(new_content)
                print("Fixed", path)

print("Total raw replacements:", count)

with open("templates/store/product/list.html", "r") as f:
    text = f.read()

import re
matches = re.findall(r'\{%[^%]*trans[^%]*%\}', text)
for m in matches:
    if '\n' in m:
        print("FOUND MALFORMED:", repr(m))


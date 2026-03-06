with open("templates/base.html", "r") as f:
    text = f.read()

import re
# check if the tags are rendering as text because they still have newlines and my script failed to replace them
count = 0
for match in re.finditer(r'\{%[^%]*trans[^%]*%\}', text):
    if '\n' in match.group():
        print("STILL BROKEN:", repr(match.group()))
        count += 1
print("Found", count, "broken tags in base.html")

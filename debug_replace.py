import re
with open("templates/base.html", "r", encoding="utf-8") as f:
    text = f.read()

def rpl(m):
    orig = m.group(0)
    new_s = ' '.join(orig.split())
    if orig != new_s:
        print("DIFF FOUND!")
        print("ORIGINAL:", repr(orig))
        print("NEW:", repr(new_s))
    return new_s

new_text = re.sub(r'\{%\s*trans\s+"[^"]*"\s*%\}', rpl, text)
print("Are they equal after substitution?", text == new_text)

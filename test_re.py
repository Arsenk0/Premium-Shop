import re
text = """<button type="submit" class="btn btn-primary" style="width: 100%; min-width: auto;">{% trans
                        "Застосувати" %}</button>"""
for match in re.finditer(r'\{%\s*trans[^%]+%\}', text, re.MULTILINE):
    print("Found:", repr(match.group(0)))
    print("Replaced:", repr(re.sub(r'\s+', ' ', match.group(0))))

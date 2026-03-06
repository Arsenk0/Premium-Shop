import re
with open("templates/base.html", "r") as f:
    text = f.read()

pattern = r'\{%\s*trans\s+"[^"]*"\s*%\}'
matches = re.findall(pattern, text)
print("Matches found:", len(matches))
for m in matches:
    if "Кабінет" in m:
        print("MATCHED KABINET:", repr(m))

raw_find = text.find("Кабінет")
if raw_find != -1:
    print("RAW KABINET FOUND AT", raw_find)
    print("CONTEXT:", repr(text[raw_find-20:raw_find+20]))


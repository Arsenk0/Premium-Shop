import re
with open("templates/store/order/create.html", "r", encoding="utf-8") as f:
    text = f.read()

text = re.sub(r'\{%\s*endif\s*%\}', '{% endif %}', text)

with open("templates/store/order/create.html", "w", encoding="utf-8") as f:
    f.write(text)

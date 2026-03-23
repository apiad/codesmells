---
rule_id: js-sec-unescaped-innerhtml
---

### Anti-Pattern #1 (Concat)
```javascript
el.innerHTML = "<div>" + content + "</div>";
```

### Anti-Pattern #2 (Template Literal)
```javascript
el.innerHTML = `Welcome ${user}`;
```

### Safe #1 (textContent)
```javascript
el.textContent = content;
```

### Safe #2 (innerText)
```javascript
el.innerText = "Processing...";
```

---
rule_id: js-sec-unescaped-innerhtml
---

### Anti-Pattern #1 (Concat)

This code example demonstrates the Unescaped innerHTML anti-pattern. Specifically, it illustrates the `Concat` case.

```javascript
el.innerHTML = "<div>" + content + "</div>";
```

### Anti-Pattern #2 (Template Literal)

This code example demonstrates the Unescaped innerHTML anti-pattern. Specifically, it illustrates the `Template Literal` case.

```javascript
el.innerHTML = `Welcome ${user}`;
```

### Safe #1 (textContent)

This code example demonstrates a safe approach for the Unescaped innerHTML issue. Specifically, it illustrates the `textContent` case.

```javascript
el.textContent = content;
```

### Safe #2 (innerText)

This code example demonstrates a safe approach for the Unescaped innerHTML issue. Specifically, it illustrates the `innerText` case.

```javascript
el.innerText = "Processing...";
```

---
id: js-sec-unescaped-innerhtml
title: Unescaped innerHTML
description: Injecting unescaped user content into `innerHTML` creates a critical Cross-Site Scripting (XSS) vulnerability. Always prefer `textContent` for plain text or use a robust sanitization library to safely handle dynamic HTML.
pre_filters:
  - "innerHTML"
tau: 0.70
---

# Unescaped innerHTML

### Anti-Pattern

```javascript
.innerHTML =
```

### Refactoring

Use `textContent` to inject plain text safely, or `createElement` and `appendChild` for safe HTML manipulation.

```javascript
$EL.textContent = $VAL
```

### Refactor Explanation
`innerHTML` parses the string as HTML, which means any `<script>` tags or `onerror` attributes in the user input will be executed by the browser. `textContent` treats the input as plain text, preventing any malicious code execution.

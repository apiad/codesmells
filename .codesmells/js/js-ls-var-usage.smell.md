---
id: js-ls-var-usage
title: Var Usage
description: The `var` keyword uses functional scope and is hoisted, which often leads to unpredictable variable visibility and subtle bugs. Modern `let` and `const` provide block-scoping, ensuring that variables are only accessible where intended.
pre_filters:
  - "var"
tau: 0.48
---

# Var Usage

### Anti-Pattern

```javascript
var $VAR = $VALUE
```

### Anti-Pattern

```javascript
var $VAR;
```

### Refactoring

Use `let` for variables that will change and `const` for those that won't.

```javascript
let $VAR = $VALUE
```

### Refactor Explanation
`var` has functional scope and is hoisted, which can lead to subtle bugs and unexpected behavior. Modern JavaScript (ES6+) introduced `let` and `const`, which provide block-scoping and make the code more predictable and safer.

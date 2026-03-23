---
id: js-ls-callback-hell
title: Callback Hell
description: Deeply nested callbacks, or the "pyramid of doom," result in opaque, difficult-to-maintain asynchronous logic. Transitioning to `async/await` or Promises flattens the structure, making asynchronous flows readable and error handling straightforward.
pre_filters:
  - "=>"
  - "function"
tau: 0.34
---

# Callback Hell

### Anti-Pattern

This code example demonstrates the Callback Hell anti-pattern.

```javascript
$F1(..., function($R1) {
    $F2(..., function($R2) {
        $F3(..., function($R3) {
            $F4(..., function($R4) {
                ...
            })
        })
    })
})
```

### Anti-Pattern

This code example demonstrates the Callback Hell anti-pattern.

```javascript
$F1(..., ($R1) => {
    $F2(..., ($R2) => {
        $F3(..., ($R3) => {
            $F4(..., ($R4) => {
                ...
            })
        })
    })
})
```

### Refactoring

Flatten the nested structure by using `async/await`.

```javascript
const $R1 = await $F1(...)
const $R2 = await $F2($R1)
const $R3 = await $F3($R2)
const $R4 = await $F4($R3)
```

### Refactor Explanation
Deep nesting is often called "the pyramid of doom." It obscures the logic and makes error handling extremely complex. `async/await` allows you to write asynchronous code that looks and behaves like synchronous code, leading to much cleaner and more maintainable logic.

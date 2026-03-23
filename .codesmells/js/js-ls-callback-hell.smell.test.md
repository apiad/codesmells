---
rule_id: js-ls-callback-hell
---

### Anti-Pattern #1 (Arrow Callbacks)

This code example demonstrates the Callback Hell anti-pattern. Specifically, it illustrates the `Arrow Callbacks` case.

```javascript
getData(1, (r1) => {
    getData(r1, (r2) => {
        getData(r2, (r3) => {
            console.log(r3);
        });
    });
});
```

### Anti-Pattern #2 (Function Callbacks)

This code example demonstrates the Callback Hell anti-pattern. Specifically, it illustrates the `Function Callbacks` case.

```javascript
getData(1, function(r1) {
    getData(r1, function(r2) {
        getData(r2, function(r3) {
            console.log(r3);
        });
    });
});
```

### Safe #1 (Async Await)

This code example demonstrates a safe approach for the Callback Hell issue. Specifically, it illustrates the `Async Await` case.

```javascript
const r1 = await getData(1);
const r2 = await getData(r1);
const r3 = await getData(r2);
```

### Safe #2 (Shallow Callback)

This code example demonstrates a safe approach for the Callback Hell issue. Specifically, it illustrates the `Shallow Callback` case.

```javascript
getData(1, (r1) => {
    console.log(r1);
});
```

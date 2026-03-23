---
rule_id: js-solid-tight-coupling
---

### Anti-Pattern #1 (New in constructor)

This code example demonstrates the Tight Coupling (New-ing dependencies) anti-pattern. Specifically, it illustrates the `New in constructor` case.

```javascript
class Order {
    constructor() {
        this.db = new Database();
    }
}
```

### Anti-Pattern #2 (New in method)

This code example demonstrates the Tight Coupling (New-ing dependencies) anti-pattern. Specifically, it illustrates the `New in method` case.

```javascript
class Order {
    save() {
        this.db = new Database();
    }
}
```

### Safe #1 (Injection)

This code example demonstrates a safe approach for the Tight Coupling (New-ing dependencies) issue. Specifically, it illustrates the `Injection` case.

```javascript
class Order {
    constructor(db) {
        this.db = db;
    }
}
```

### Safe #2 (Factory Injection)

This code example demonstrates a safe approach for the Tight Coupling (New-ing dependencies) issue. Specifically, it illustrates the `Factory Injection` case.

```javascript
class Order {
    constructor(dbFactory) {
        this.db = dbFactory.create();
    }
}
```

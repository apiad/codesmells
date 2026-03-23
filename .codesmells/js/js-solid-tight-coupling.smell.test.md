---
rule_id: js-solid-tight-coupling
---

### Anti-Pattern #1 (New in constructor)
```javascript
class Order {
    constructor() {
        this.db = new Database();
    }
}
```

### Anti-Pattern #2 (New in method)
```javascript
class Order {
    save() {
        this.db = new Database();
    }
}
```

### Safe #1 (Injection)
```javascript
class Order {
    constructor(db) {
        this.db = db;
    }
}
```

### Safe #2 (Factory Injection)
```javascript
class Order {
    constructor(dbFactory) {
        this.db = dbFactory.create();
    }
}
```

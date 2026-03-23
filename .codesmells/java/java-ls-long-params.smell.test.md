---
rule_id: java-ls-long-params
---

### Anti-Pattern #1 (5 Parameters)

This code example demonstrates the Long Parameter List anti-pattern. Specifically, it illustrates the `5 Parameters` case.

```java
public void registerUser(String username, String password, String email, String firstName, String lastName) {
    // ...
}
```

### Safe #1 (3 Parameters)

This code example demonstrates a safe approach for the Long Parameter List issue. Specifically, it illustrates the `3 Parameters` case.

```java
public void login(String username, String password, boolean rememberMe) {
    // ...
}
```

### Safe #2 (Parameter Object)

This code example demonstrates a safe approach for the Long Parameter List issue. Specifically, it illustrates the `Parameter Object` case.

```java
public void registerUser(UserRegistrationDto registration) {
    // ...
}
```

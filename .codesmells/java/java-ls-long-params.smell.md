---
id: java-ls-long-params
title: Long Parameter List
description: Methods with too many parameters are difficult to understand and maintain. Consider grouping related parameters into a single object (Parameter Object pattern).
pre_filters:
  - "("
  - ","
tau: 0.42
---

# Long Parameter List

### Anti-Pattern

This code example demonstrates the Long Parameter List anti-pattern.

```java
$MODIFIERS $RETURN $NAME($T1 $P1, $T2 $P2, $T3 $P3, $T4 $P4, $T5 $P5) {
```

### Refactoring

Group related parameters into a descriptive class or use a Builder pattern.

```java
$MODIFIERS $RETURN $NAME($DTO $DATA) {
```

### Refactor Explanation
A long list of parameters is often a sign that a method has too many responsibilities or that the data it operates on is highly coupled. By introducing a Parameter Object, you improve code readability, make the method signature more stable, and provide a natural place for validation logic.

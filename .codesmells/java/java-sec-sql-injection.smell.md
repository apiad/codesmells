---
id: java-sec-sql-injection
title: SQL Injection
description: Concatenating user input directly into SQL queries is a critical security vulnerability. Use `PreparedStatement` with parameterized queries to prevent SQL Injection attacks.
pre_filters:
  - "SELECT"
  - "+"
---

# SQL Injection

### Anti-Pattern

This code example demonstrates the SQL Injection anti-pattern.

```java
String $QUERY = "SELECT * FROM $TABLE WHERE $COL = '" + $INPUT + "'";
```

### Refactoring

Use parameterized queries with `PreparedStatement`.

```java
String query = "SELECT * FROM $TABLE WHERE $COL = ?";
PreparedStatement pstmt = conn.prepareStatement(query);
pstmt.setString(1, $INPUT);
```

### Refactor Explanation
String concatenation allows an attacker to manipulate the SQL command structure by injecting malicious SQL fragments (e.g., `' OR '1'='1`). Parameterized queries treat user input as data only, ensuring that the database engine never executes it as code.

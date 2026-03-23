---
rule_id: java-sec-sql-injection
---

### Anti-Pattern #1 (Simple Concat)

This code example demonstrates the SQL Injection anti-pattern. Specifically, it illustrates the `Simple Concat` case.

```java
String sql = "SELECT * FROM users WHERE id = '" + userId + "'";
```

### Anti-Pattern #2 (Multiple Concat)

This code example demonstrates the SQL Injection anti-pattern. Specifically, it illustrates the `Multiple Concat` case.

```java
String query = "SELECT name FROM products WHERE category = '" + cat + "' AND price < " + maxPrice;
```

### Safe #1 (Parameterized)

This code example demonstrates a safe approach for the SQL Injection issue. Specifically, it illustrates the `Parameterized` case.

```java
String sql = "SELECT * FROM users WHERE id = ?";
PreparedStatement st = conn.prepareStatement(sql);
st.setString(1, userId);
```

### Safe #2 (Constant)

This code example demonstrates a safe approach for the SQL Injection issue. Specifically, it illustrates the `Constant` case.

```java
String sql = "SELECT * FROM roles WHERE name = 'ADMIN'";
```

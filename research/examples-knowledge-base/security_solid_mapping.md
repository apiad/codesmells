# Security & SOLID Violations as Detectable Patterns

This document maps abstract security and design principles to concrete code patterns that can be detected via CodeSmells rules.

## 1. Security (OWASP-inspired)

| Vulnerability | Detectable Pattern | Bad Example (Smell) | Good Example (Safe) |
| :--- | :--- | :--- | :--- |
| **Hardcoded Secrets** | Assignment of high-entropy strings or keyword matches. | `api_key = "AIzaSy..."` | `api_key = os.getenv("API_KEY")` |
| **SQL Injection** | String concatenation/f-strings in SQL queries. | `db.execute(f"SELECT * FROM users WHERE id = {uid}")` | `db.execute("SELECT * FROM users WHERE id = %s", (uid,))` |
| **Command Injection** | Using `os.system` or `subprocess` with shell=True. | `os.system("rm -rf " + user_path)` | `subprocess.run(["rm", "-rf", user_path])` |
| **XSS (HTML)** | Unescaped user input in templates or `innerHTML`. | `el.innerHTML = "<h1>Welcome " + user_name + "</h1>"` | `el.textContent = user_name` |
| **Weak Crypto** | Use of MD5, SHA1 for passwords or sensitive data. | `hash = hashlib.md5(password.encode()).hexdigest()` | `hash = argon2.hash(password)` |

## 2. SOLID Principle Violations

### Single Responsibility Principle (SRP)
*   **Smell:** "And" functions/classes (e.g., `save_and_email`).
*   **Pattern:** Multiple blocks of unrelated logic in one function.
*   **Bad:** One function handles database I/O, business logic, and UI updates.
*   **Good:** Discrete functions for each task.

### Open/Closed Principle (OCP)
*   **Smell:** Deep `if/elif` or `switch` chains on type or category.
*   **Pattern:** Hardcoded checks for specific types that require modification when a new type is added.
*   **Bad:** `if type == 'cat': ... elif type == 'dog': ...`
*   **Good:** Polymorphism or strategy pattern.

### Liskov Substitution Principle (LSP)
*   **Smell:** `NotImplementedError` or `return None` in overridden methods.
*   **Pattern:** A subclass that breaks the contract of the parent class.
*   **Bad:** `class Square(Rectangle): def set_width(w): self.w = w; self.h = w` (breaks Rectangle's contract).
*   **Good:** Subclasses that are fully interchangeable with their base classes.

### Interface Segregation Principle (ISP)
*   **Smell:** "Fat" interfaces with many unrelated methods.
*   **Pattern:** Classes forced to implement methods they don't use.
*   **Bad:** `interface Worker { void work(); void eat(); void sleep(); }`
*   **Good:** Small, focused interfaces like `Workable`, `Eatable`.

### Dependency Inversion Principle (DIP)
*   **Smell:** Hardcoded instantiation of low-level dependencies.
*   **Pattern:** Using `new ConcreteClass()` inside a high-level module.
*   **Bad:** `class Service { repo = new DatabaseRepo(); }`
*   **Good:** Injecting the dependency: `class Service { constructor(repo) { this.repo = repo; } }`

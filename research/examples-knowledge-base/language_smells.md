# Language-Specific Code Smells & Anti-Patterns

This document identifies high-impact code smells for mainstream programming languages, focusing on patterns detectable via fuzzy structural alignment or probabilistic lexing.

## 1. Python
*   **Broad Exception Catching:** Catching `Exception` or `BaseException` instead of specific errors.
    *   *Why:* Masking bugs and making debugging impossible.
    *   *Bad:* `try: ... except: pass`
    *   *Good:* `try: ... except ValueError: ...`
*   **Mutable Default Arguments:** Using `[]` or `{}` as default values in function signatures.
    *   *Why:* The default object is shared across all calls, leading to persistent state bugs.
    *   *Bad:* `def add_to(item, list=[]):`
    *   *Good:* `def add_to(item, list=None):`
*   **Non-idiomatic Loops:** Using `range(len(seq))` to iterate over indices.
    *   *Why:* Less readable and slower than direct iteration or `enumerate`.
    *   *Bad:* `for i in range(len(mylist)): x = mylist[i]`
    *   *Good:* `for i, x in enumerate(mylist): ...`

## 2. JavaScript / TypeScript
*   **Callback Hell:** Deeply nested anonymous functions for asynchronous operations.
    *   *Why:* Extremely hard to read, maintain, and handle errors.
    *   *Bad:* `getData(a => { getMore(b => { ... }) })`
    *   *Good:* `const a = await getData(); const b = await getMore();`
*   **'Any'-script (TS):** Overuse of the `any` type to bypass the compiler.
    *   *Why:* Defeats the purpose of TypeScript, losing type safety.
    *   *Bad:* `function process(data: any) { return data.foo; }`
    *   *Good:* `interface Data { foo: string; } function process(data: Data) { ... }`
*   **Var Usage:** Using `var` instead of `let` or `const`.
    *   *Why:* Unpredictable hoisting and function-scoping behavior.
    *   *Bad:* `for (var i = 0; i < 10; i++) { ... }`
    *   *Good:* `for (let i = 0; i < 10; i++) { ... }`

## 3. C / C++
*   **Unsafe Pointer Arithmetic:** Directly manipulating memory addresses without bounds checking.
    *   *Why:* Primary source of buffer overflows and memory corruption.
    *   *Bad:* `char *ptr = buffer; ptr += offset; *ptr = 'a';`
    *   *Good:* Use `std::vector` or `std::array` with `.at()`.
*   **Manual Memory Management (No RAII):** Using `malloc/free` or `new/delete` without smart pointers.
    *   *Why:* Leads to memory leaks and use-after-free vulnerabilities.
    *   *Bad:* `int* arr = new int[10]; if (error) return; delete[] arr;`
    *   *Good:* `std::unique_ptr<int[]> arr = std::make_unique<int[]>(10);`
*   **Lack of Const Correctness:** Passing objects by non-const reference when they shouldn't change.
    *   *Why:* Harder to reason about side effects and prevents compiler optimizations.
    *   *Bad:* `void print(std::string& s);`
    *   *Good:* `void print(const std::string& s);`

## 4. Java / C#
*   **God Objects:** Single classes that perform too many disparate tasks.
    *   *Why:* Violates Single Responsibility Principle (SRP) and creates high coupling.
    *   *Bad:* `class AppManager { void saveUser(); void processPayment(); void sendEmail(); }`
    *   *Good:* Separate into `UserRepository`, `PaymentService`, and `EmailNotifier`.
*   **Deep Inheritance Hierarchies:** Using inheritance for code reuse instead of composition.
    *   *Why:* Leads to "Fragile Base Class" problem and tight coupling.
    *   *Bad:* `class Employee extends Person extends LivingBeing ...`
    *   *Good:* Use interfaces and composition (`has-a` instead of `is-a`).
*   **Empty Catch Blocks:** Catching exceptions and doing nothing with them.
    *   *Why:* Silently failing makes root cause analysis impossible.
    *   *Bad:* `try { ... } catch (Exception e) {}`
    *   *Good:* Log the error or rethrow a custom exception.

## 5. Rust
*   **Unnecessary Unwraps:** Frequent use of `.unwrap()` instead of proper error handling.
    *   *Why:* Causes the program to panic (crash) on unexpected input.
    *   *Bad:* `let val = my_option.unwrap();`
    *   *Good:* `let val = my_option.ok_or("error")?;`
*   **Excessive Cloning:** Using `.clone()` to avoid borrow checker issues.
    *   *Why:* Significant performance overhead and hides ownership design flaws.
    *   *Bad:* `do_something(data.clone());`
    *   *Good:* Pass by reference `do_something(&data);`
*   **Large Unsafe Blocks:** Wrapping too much code in `unsafe {}`.
    *   *Why:* Circumvents Rust's safety guarantees over a broad area.
    *   *Bad:* `unsafe { /* 100 lines of complex logic */ }`
    *   *Good:* Minimize unsafe code to specific, audited primitives.

## 6. Go
*   **Interface{} Abuse:** Using `interface{}` (or `any`) instead of concrete types or generics.
    *   *Why:* Loses type safety and requires expensive run-time type assertions.
    *   *Bad:* `func Do(v interface{}) { ... }`
    *   *Good:* Use generics `func Do[T any](v T) { ... }` or specific interfaces.
*   **Ignoring Errors:** Using `_` to discard error returns.
    *   *Why:* Swallows failures and leads to inconsistent program state.
    *   *Bad:* `val, _ := compute()`
    *   *Good:* `val, err := compute(); if err != nil { ... }`
*   **Deep Nesting (Error Handling):** Multiple levels of `if err != nil` without early returns.
    *   *Why:* Creates "arrow code" that is hard to follow.
    *   *Bad:* `if err == nil { if err2 == nil { ... } }`
    *   *Good:* `if err != nil { return err }; if err2 != nil { return err2 }; ...`

## 7. HTML / CSS
*   **Div Soup (Non-semantic HTML):** Using `<div>` for everything instead of `<header>`, `<nav>`, `<article>`, etc.
    *   *Why:* Bad for accessibility (A11y) and SEO.
    *   *Bad:* `<div class="nav">...</div>`
    *   *Good:* `<nav>...</nav>`
*   **!important Overuse (CSS):** Using `!important` to force style overrides.
    *   *Why:* Breaks the cascade and makes styles impossible to maintain.
    *   *Bad:* `.btn { color: red !important; }`
    *   *Good:* Use more specific selectors or refactor the cascade.
*   **Magic Numbers (CSS):** Hardcoded pixel values for layout instead of relative units.
    *   *Why:* Breaks responsiveness and consistent spacing.
    *   *Bad:* `padding: 13px; margin-left: 147px;`
    *   *Good:* `padding: 1rem; margin-left: 10%;`

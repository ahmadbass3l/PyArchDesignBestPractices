# 📦 IoC Container & Dependency Injection

## What is IoC?

**Inversion of Control (IoC)** is a design principle where the control of creating and wiring objects is transferred from the application code to a **container**.

Instead of a class creating its own dependencies:
```python
# ❌ Without IoC — UserService creates its own dependencies
class UserService:
    def __init__(self):
        self.logger = ConsoleLogger()       # hardcoded
        self.email = SmtpEmailSender()      # hardcoded
```

The container injects them from the outside:
```python
# ✅ With IoC — dependencies are injected by the container
class UserService:
    def __init__(self, logger: ILogger, email_sender: IEmailSender):
        self.logger = logger           # injected
        self.email_sender = email_sender   # injected
```

---

## Concepts Covered

| Concept | Description |
|---|---|
| **IoC Container** | Central registry that builds and wires all objects |
| **Dependency Injection** | Dependencies passed in via constructor, not created internally |
| **Abstract Base Classes** | Python `ABC` used to define contracts / interfaces |
| **Singleton scope** | One shared instance for the entire app lifetime |
| **Transient scope** | A fresh instance on every `resolve()` call |
| **Composition Root** | Single place where all concrete classes are wired together |

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────┐
│                     IoCContainer                        │
│  - register(name, factory, singleton)                   │
│  - resolve(name) → builds or returns cached instance    │
└────────────────────────┬────────────────────────────────┘
                         │ resolves
        ┌────────────────┼─────────────────┐
        ▼                ▼                 ▼
 ┌─────────────┐  ┌──────────────┐  ┌──────────────────┐
 │  ILogger    │  │ IEmailSender │  │  IUserService    │
 │ (abstract)  │  │  (abstract)  │  │   (abstract)     │
 └──────┬──────┘  └──────┬───────┘  └────────┬─────────┘
        │                │                    │
        ▼                ▼                    ▼
 ┌──────────────┐ ┌──────────────────┐ ┌─────────────┐
 │ConsoleLogger │ │ SmtpEmailSender  │ │ UserService │
 │  (concrete)  │ │   (concrete)     │ │  (concrete) │
 └──────────────┘ └──────────────────┘ └─────────────┘
```

---

## How to Run

```bash
python ioc_container.py
```

### Expected Output

```
[LOG] Registering user: alice@example.com
[LOG] Sending email to 'alice@example.com' | Body: "Welcome aboard! 🎉"
[LOG] User 'alice@example.com' registered successfully.

[LOG] Registering user: bob@example.com
[LOG] Sending email to 'bob@example.com' | Body: "Welcome aboard! 🎉"
[LOG] User 'bob@example.com' registered successfully.

Same logger instance? True
Same service instance? False
```

---

## Key Takeaway

> The application never calls `ClassName()` directly.
> The container is the **single place** responsible for building and wiring all objects.
> Swap any implementation by changing **one line** in the registration block.

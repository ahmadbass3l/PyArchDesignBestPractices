# 🐍 Python Architecture Design Patterns

A curated, hands-on collection of **software architecture design patterns and best practices** implemented in Python.

Each sub-project is **self-contained**, **heavily commented**, and built to be a clear,
practical reference — not just theory.

---

## 🎯 Purpose

Good architecture makes code:
- Easier to **test** and **maintain**
- More **flexible** to change
- Clearer to **reason about** as it grows

This repository exists to document, demonstrate, and collect those principles in pure Python —
from foundational patterns to advanced architectural concepts.

---

## 📦 Sub-Projects

| # | Pattern | Folder | Concepts Covered |
|---|---------|--------|------------------|
| 01 | **IoC Container** | [`/ioc-container`](/ioc-container) | Inversion of Control, Dependency Injection, Abstract Base Classes, Singleton vs Transient scopes |
| ... | *more coming* | — | — |

---

## 🏗️ Patterns Roadmap

- [x] IoC Container & Dependency Injection
- [ ] Repository Pattern
- [ ] Unit of Work
- [ ] Domain-Driven Design (DDD) building blocks
- [ ] Clean Architecture (layers)
- [ ] CQRS (Command Query Responsibility Segregation)
- [ ] Event-Driven Architecture
- [ ] Service Locator (and why to avoid it)
- [ ] Factory & Abstract Factory
- [ ] Decorator Pattern for cross-cutting concerns (logging, caching)

---

## 🗂️ Project Structure

```
python-arch-patterns/
│
├── ioc-container/            # IoC Container & Dependency Injection
│   ├── ioc_container.py      # Full example with ABC, diagrams, comments
│   └── README.md             # Pattern explanation
│
├── repository-pattern/       # (coming soon)
├── clean-architecture/       # (coming soon)
│
└── README.md                 # This file
```

---

## ✅ Principles Behind Every Sub-Project

Every example in this repo follows these rules:

1. **Program to abstractions** — code depends on interfaces, not concrete classes
2. **Single Responsibility** — each class does one thing well
3. **Dependency Inversion** — high-level modules don't depend on low-level modules
4. **Self-documenting** — diagrams and comments live inside the code itself
5. **Runnable out of the box** — no external dependencies unless strictly necessary

---

## 🚀 How to Run Any Sub-Project

Each sub-project is a standalone Python file or folder. No framework required.

```bash
# Clone the repo
git clone https://github.com/ahmadbass3l/python-arch-patterns.git
cd python-arch-patterns

# Run any example directly
python ioc-container/ioc_container.py
```

---

## 🤝 Contributing

Found a pattern that belongs here? Feel free to open an issue or a pull request.
All contributions should follow the same standards: self-contained, well-commented, and runnable.

---

## 📄 License

MIT — free to use, learn from, and share.

"""
IoC Container Example — using Python Abstract Base Classes (ABC)

ARCHITECTURE DIAGRAM:
=====================

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
   └─────���────────┘ └──────────────────┘ └─────────────┘
          ▲                 ▲                   │
          │                 │     depends on    │
          └─────────────────┴───────────────────┘

DEPENDENCY FLOW:
================

  UserService
    ├── depends on → ILogger       → resolved as ConsoleLogger   (singleton)
    └── depends on → IEmailSender  → resolved as SmtpEmailSender (singleton)
                          └── depends on → ILogger → same singleton instance ♻️

SCOPES:
=======
  Singleton  → one shared instance for the entire app lifetime
  Transient  → a brand new instance on every resolve() call
"""

from abc import ABC, abstractmethod


# ══════════════════════════════════════════════════════════════
#  1. IoC CONTAINER
#     Responsible for registering and resolving all services.
#     Nothing outside this container should call ClassName() directly.
# ══════════════════════════════════════════════════════════════

class IoCContainer:
    def __init__(self):
        # Stores all registered service recipes: name → {factory, singleton}
        self._registry: dict = {}
        # Stores already-built singleton instances: name → instance
        self._singletons: dict = {}

    def register(self, name: str, factory, singleton: bool = False) -> None:
        """
        Register a service by name.

        Args:
            name:      Unique key used to resolve this service later.
            factory:   A callable (lambda or function) that accepts the
                       container (c) and returns a built instance.
            singleton: If True, the instance is built once and reused.
                       If False (default), a new instance is created on
                       every resolve() call (transient behaviour).
        """
        self._registry[name] = {"factory": factory, "singleton": singleton}

    def resolve(self, name: str):
        """
        Resolve (build or retrieve) a registered service by name.

        The container passes itself (self) into the factory so the
        factory can recursively resolve its own dependencies.

        Args:
            name: The key used when the service was registered.

        Returns:
            A fully built service instance with all dependencies injected.
        """
        if name not in self._registry:
            raise KeyError(f"[Container] Service '{name}' is not registered.")

        entry = self._registry[name]

        # ── Singleton: build once, cache, return the same object forever ──
        if entry["singleton"]:
            if name not in self._singletons:
                # Build the instance and cache it
                self._singletons[name] = entry["factory"](self)
            return self._singletons[name]

        # ── Transient: build a fresh instance every time ──
        return entry["factory"](self)


# ══════════════════════════════════════════════════════════════
#  2. ABSTRACTIONS  (the contracts / interfaces)
#     Define *what* a service must do, not *how* it does it.
#     All application code should depend on these, never on
#     the concrete classes below.
# ══════════════════════════════════════════════════════════════

class ILogger(ABC):
    """Contract: any logger must implement log()."""

    @abstractmethod
    def log(self, message: str) -> None:
        """Log a message somewhere."""
        ...


class IEmailSender(ABC):
    """Contract: any email sender must implement send()."""

    @abstractmethod
    def send(self, to: str, body: str) -> None:
        """Send an email to an address with a body."""
        ...


class IUserService(ABC):
    """Contract: any user service must implement register_user()."""

    @abstractmethod
    def register_user(self, email: str) -> None:
        """Register a new user by email."""
        ...


# ══════════════════════════════════════════════════════════════
#  3. CONCRETE IMPLEMENTATIONS
#     These are the real classes that fulfil the contracts above.
#     You can swap any of these for a different implementation
#     (e.g. FileLogger, MockEmailSender) without touching any
#     other part of the application.
# ══════════════════════════════════════════════════════════════

class ConsoleLogger(ILogger):
    """Logs messages to the console (stdout)."""

    def log(self, message: str) -> None:
        print(f"[LOG] {message}")


class SmtpEmailSender(IEmailSender):
    """
    Sends emails via SMTP.
    Depends on ILogger — injected by the container, not created here.
    """

    def __init__(self, logger: ILogger):
        # The logger is injected — SmtpEmailSender does NOT know which
        # concrete logger it receives. It only knows it can call .log()
        self._logger = logger

    def send(self, to: str, body: str) -> None:
        # In a real app this would open an SMTP connection, etc.
        self._logger.log(f"Sending email to '{to}' | Body: \"{body}\"")


class UserService(IUserService):
    """
    Handles user registration logic.
    Depends on ILogger and IEmailSender — both injected by the container.
    """

    def __init__(self, logger: ILogger, email_sender: IEmailSender):
        # Both dependencies are abstractions — UserService has no idea
        # which concrete classes are wired in. Swap freely via the container.
        self._logger = logger
        self._email_sender = email_sender

    def register_user(self, email: str) -> None:
        self._logger.log(f"Registering user: {email}")
        self._email_sender.send(to=email, body="Welcome aboard! 🎉")
        self._logger.log(f"User '{email}' registered successfully.")


# ══════════════════════════════════════════════════════════════
#  4. COMPOSITION ROOT  (wire everything together)
#     This is the ONLY place in the app where concrete class
#     names appear. Everything else talks to abstractions.
#
#     Registration order does not matter — factories are lazy.
#     The container only builds an object when resolve() is called.
# ══════════════════════════════════════════════════════════════

container = IoCContainer()

# Register the logger as a singleton:
# → ConsoleLogger() is built once and reused everywhere.
container.register(
    "logger",
    lambda c: ConsoleLogger(),
    singleton=True
)

# Register the email sender as a singleton:
# → Needs a logger, so it asks the container: c.resolve("logger")
# → Returns the same ConsoleLogger singleton (not a new one).
container.register(
    "email_sender",
    lambda c: SmtpEmailSender(
        logger=c.resolve("logger")   # ← container injects the logger
    ),
    singleton=True
)

# Register the user service as transient (singleton=False by default):
# → A fresh UserService is created on every resolve() call.
# → Its dependencies (logger, email_sender) are still singletons.
container.register(
    "user_service",
    lambda c: UserService(
        logger=c.resolve("logger"),              # ← same singleton logger
        email_sender=c.resolve("email_sender")   # ← same singleton sender
    )
    # singleton=False → transient (default)
)


# ══════════════════════════════════════════════════════════════
#  5. APPLICATION ENTRY POINT
#     The app only ever calls container.resolve().
#     It never instantiates services itself.
# ══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    # The container builds the full object graph automatically:
    #   UserService → SmtpEmailSender → ConsoleLogger
    #             └──────────────────→ ConsoleLogger (same instance ♻️)
    user_service: IUserService = container.resolve("user_service")
    user_service.register_user("alice@example.com")

    print()  # spacing

    # Resolving again → new UserService (transient), but same singletons
    user_service_2: IUserService = container.resolve("user_service")
    user_service_2.register_user("bob@example.com")

    print()  # spacing

    # Prove singleton behaviour
    logger_a = container.resolve("logger")
    logger_b = container.resolve("logger")
    print(f"Same logger instance? {logger_a is logger_b}")    # → True

    service_a = container.resolve("user_service")
    service_b = container.resolve("user_service")
    print(f"Same service instance? {service_a is service_b}") # → False

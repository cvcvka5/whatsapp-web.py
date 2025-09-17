# whatsapp-web.py

> ⚠️ **Work in Progress:** This project is under active development. Features may be incomplete and APIs may change.


A Python client for interacting with [WhatsApp Web](https://web.whatsapp.com/) using Playwright. This library provides QR-based authentication, session management, and an event-driven API for automating and interacting with chats, messages, and media.

## Key Techniques

* **Playwright-based browser automation** for headless and headed browser control. ([MDN: Browser Automation](https://developer.mozilla.org/en-US/docs/Web/API/Automation))
* **Event-driven architecture** using a custom `EventEmitter` pattern to manage asynchronous events like incoming messages, connection updates, and status changes.
* **Dynamic JavaScript module injection** to interact with WhatsApp Web internals without relying on the official API.
* **TypedDict and data modeling** for structured type-safe access to contacts, groups, and messages in Python.

## Notable Libraries & Technologies

* **[Playwright](https://playwright.dev/python/)** for full browser automation.
* **Python `typing` module** for runtime type checking and clarity in data models.
* **Modern JS techniques**: dynamic module injection, eval-based script execution, and DOM querying to interface with WhatsApp Web.
* **Custom QR login handling** and session persistence to maintain state between script runs.
* **[whatsapp-web.js](https://github.com/pedroslopez/whatsapp-web.js)** as a reference to WhatsApp's internal api. 

## Project Structure

```
wawebpy/
├── client.py           # Main client and initialization
├── structures/         # Chat, Contact, Group models, and event handling
├── util/               # Utility scripts and helpers for JS injection
└── __init__.py
```

* `structures/` contains core Python abstractions for Contacts, Groups, Chats, and Events.
* `util/` includes helpers for safely injecting and executing JavaScript inside the WhatsApp Web environment.

## Contributions

We welcome contributions of any kind:

* Bug fixes
* Feature requests
* Documentation improvements
* Examples or tutorials
* Code refactoring

If you have ideas or improvements, feel free to open a pull request. Every contribution helps strengthen this project and supports professional developers in building automation on top of WhatsApp Web.
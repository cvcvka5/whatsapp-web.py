# WhatsApp Web Python Client

A Python client for interacting with WhatsApp Web using Playwright.
This project allows QR-based authentication and aims to provide a framework for automating or interacting with WhatsApp Web programmatically.

> ⚠️ **Work in Progress:** This project is under active development. Features may be incomplete and APIs may change.

## Features

* QR code authentication
* Event-based architecture with `EventEmitter`
* Supports multiple authentication methods:

  * `NoAuth` (QR-based login)
  * `LegacySessionAuth` (planned)
  * `LocalAuth` (planned)
* Playwright-based browser automation

## Usage

```python
The package is not yet functional. Keep contributing to speed up the process.
```

## Contributing

We welcome contributions! This project is a work-in-progress, so your help is invaluable. Here are ways you can contribute:

1. **Bug Reports:** Open an issue if you find a bug, unexpected behavior, or have questions.
2. **Feature Requests:** Suggest new features or improvements to existing functionality.
3. **Code Contributions:**

   * Fork the repository.
   * Create a feature branch (`git checkout -b feature-name`).
   * Make your changes and commit them (`git commit -m 'Add new feature'`).
   * Push to your branch (`git push origin feature-name`).
   * Open a Pull Request for review.
4. **Documentation:** Improve or expand the documentation to help new contributors understand the project.

**Please Note:** APIs may change frequently, and some features are not yet implemented. Contributions that help stabilize and document the project are highly appreciated.

## Acknowledgements

This project is inspired by whatsapp-web.js
, a Node.js library that connects to WhatsApp Web. While this implementation is in Python, the core idea and approach are influenced by the work done in the JavaScript community.

## License

This project is open-source. Please check the LICENSE file for details.

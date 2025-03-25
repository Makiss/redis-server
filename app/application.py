"""Main application implementation."""


class Application:
    """A simple application."""

    def __init__(self, config=None):
        """Initialize the application.

        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        self.running = False

    def start(self):
        """Start the application."""
        print("Starting application")
        self.running = True

    def stop(self):
        """Stop the application."""
        print("Stopping application")
        self.running = False

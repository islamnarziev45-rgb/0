"""Bothost entry point for the Tez VPN Telegram bot."""
import sys

from bot import main


if __name__ == "__main__":
    # Make startup and polling diagnostics visible immediately in container logs.
    sys.stdout.reconfigure(line_buffering=True)
    sys.stderr.reconfigure(line_buffering=True)
    main()


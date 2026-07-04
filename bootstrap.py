"""One-off scaffolder that ensures the project's folder structure exists.

Not part of the application runtime — run manually (`python bootstrap.py`)
after cloning if any package folders or __init__.py files are missing.
"""

from pathlib import Path

PROJECT_STRUCTURE: list[str] = [
    "core",
    "ui",
    "providers",
    "browser",
    "skills",
    "workflows",
    "plugins",
    "memory",
    "config",
    "data",
    "logs",
]

INIT_PACKAGES: list[str] = [
    "core",
    "ui",
    "providers",
    "browser",
    "skills",
    "workflows",
    "plugins",
    "memory",
    "config",
]


def create_project() -> None:
    """Create any missing package folders and their `__init__.py` files."""
    root = Path(__file__).parent

    print("\n===================================")
    print(" AI Agent Studio Bootstrap")
    print("===================================\n")

    for folder in PROJECT_STRUCTURE:
        path = root / folder
        path.mkdir(exist_ok=True)

    for package in INIT_PACKAGES:
        init_file = root / package / "__init__.py"
        init_file.touch(exist_ok=True)

    print("Project structure verified successfully.")


if __name__ == "__main__":
    create_project()

from pathlib import Path

PROJECT_STRUCTURE = [
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

INIT_PACKAGES = [
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


def create_project():
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
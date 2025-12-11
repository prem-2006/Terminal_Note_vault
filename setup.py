from setuptools import setup, find_packages

setup(
    name="terminal-note-vault",
    version="0.1.0",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    entry_points={
        "console_scripts": [
            "vault=terminal_vault.cli.main:main",
        ],
    },
    python_requires=">=3.6",
)

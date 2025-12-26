"""Language detection for automatic linter selection."""

from pathlib import Path


class LanguageDetector:
    """Detects programming languages from file paths."""

    # Language to file extension mapping
    LANGUAGE_EXTENSIONS: dict[str, set[str]] = {
        "python": {".py", ".pyi", ".pyw"},
        "javascript": {".js", ".jsx", ".mjs", ".cjs"},
        "typescript": {".ts", ".tsx"},
        "java": {".java"},
        "go": {".go"},
        "rust": {".rs"},
        "cpp": {".cpp", ".cc", ".cxx", ".hpp", ".h", ".hxx"},
        "c": {".c", ".h"},
        "ruby": {".rb"},
        "php": {".php"},
        "swift": {".swift"},
        "kotlin": {".kt", ".kts"},
        "scala": {".scala"},
        "dart": {".dart"},
        "r": {".r", ".R"},
        "shell": {".sh", ".bash", ".zsh", ".fish"},
    }

    # Language to linter mapping (zero new dependencies)
    LANGUAGE_LINTERS: dict[str, list[str]] = {
        "python": ["ruff", "bandit", "pylint", "flake8", "mypy", "safety", "pip-audit", "coverage"],
        "html": ["html-accessibility"],  # Custom tool, no dependency
        "javascript": [],  # No JS linters yet (would require Node.js)
        "typescript": [],  # No TS linters yet
        "java": [],  # No Java linters yet
        "go": [],  # No Go linters yet
        "rust": [],  # No Rust linters yet
    }

    @classmethod
    def detect_language(cls, file_path: str) -> str | None:
        """
        Detect language from file path.

        Args:
            file_path: Path to file

        Returns:
            Language name or None
        """
        path = Path(file_path)
        extension = path.suffix.lower()

        for language, extensions in cls.LANGUAGE_EXTENSIONS.items():
            if extension in extensions:
                return language

        return None

    @classmethod
    def detect_languages(cls, file_paths: list[str]) -> set[str]:
        """
        Detect languages from multiple file paths.

        Args:
            file_paths: List of file paths

        Returns:
            Set of detected languages
        """
        languages = set()
        for file_path in file_paths:
            language = cls.detect_language(file_path)
            if language:
                languages.add(language)
        return languages

    @classmethod
    def get_linters_for_language(cls, language: str) -> list[str]:
        """
        Get recommended linters for a language.

        Args:
            language: Language name

        Returns:
            List of linter names
        """
        return cls.LANGUAGE_LINTERS.get(language.lower(), [])

    @classmethod
    def get_linters_for_files(cls, file_paths: list[str]) -> list[str]:
        """
        Get recommended linters for files.

        Args:
            file_paths: List of file paths

        Returns:
            List of linter names
        """
        languages = cls.detect_languages(file_paths)
        linters = set()

        for language in languages:
            linters.update(cls.get_linters_for_language(language))

        return list(linters)

    @classmethod
    def find_config_files(cls, path: str) -> dict[str, Path]:
        """
        Find existing linter configuration files.

        Args:
            path: Path to search

        Returns:
            Dictionary mapping linter names to config file paths
        """
        path_obj = Path(path)
        if path_obj.is_file():
            search_dir = path_obj.parent
        else:
            search_dir = path_obj

        config_files = {}

        # Common config file patterns
        config_patterns = {
            "ruff": ["ruff.toml", ".ruff.toml", "pyproject.toml"],
            "pylint": [".pylintrc", "pylintrc", "setup.cfg", "pyproject.toml"],
            "flake8": [".flake8", "setup.cfg", "tox.ini", "pyproject.toml"],
            "bandit": ["bandit.yaml", ".bandit", "setup.cfg", "pyproject.toml"],
            "mypy": ["mypy.ini", ".mypy.ini", "setup.cfg", "pyproject.toml"],
        }

        # Walk up directory tree
        current = search_dir
        while current != current.parent:
            for linter, patterns in config_patterns.items():
                if linter not in config_files:
                    for pattern in patterns:
                        config_path = current / pattern
                        if config_path.exists():
                            config_files[linter] = config_path
                            break
            current = current.parent

        return config_files

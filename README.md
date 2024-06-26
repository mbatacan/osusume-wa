### 🚧 Under construction 🚧
# [anime-ranking-app](https://osusume-wa.streamlit.app/)
Feature 1: NLP
- figure out pulling episode reviews data for one anime (one piece)
- perform sentiment analysis on reviews
- LLM to generate overall sentiment on episode
- Generate a episode success metric of the anime episodes

Feature 2: Reccomendations
- save small database of seasonal animes
- implement a reccomender based on a user's anime list
- possible learn to rank implementatiopn


## Quick Start

## homebrew compatibility with macOS need to look into homebrew for windows/linux

To start, install the required and recommended libraries.

1. Install [Poetry](https://python-poetry.org/docs/#installing-with-the-official-installer)
2. Install dependencies:

```bash
poetry install
```

### Contributing

Before committing anything to the repository, set up our pre-commit hooks:

```bash
pre-commit install
```

### VSCode Extensions

If developing in VSCode (highly recommended), add the following extensions for linting, type checking, and code formatting:

- [Python](https://marketplace.visualstudio.com/items?itemName=ms-python.python): IntelliSense (Pylance), Linting, Debugging (multi-threaded, remote), Jupyter Notebooks, code
- [Ruff](https://marketplace.visualstudio.com/items?itemName=charliermarsh.ruff): A Visual Studio Code extension with support for the Ruff linter.

# GitHub Repository Analyzer

This script analyzes GitHub repository activity (commits, issues, maintainer responses) to determine if a project is "Live", "Stagnant", or "Dead".

## Setup

1.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## Usage

1.  **Run the script:**
    ```bash
    python main.py <github_repository_url>
    ```
    *Example:* `python main.py https://github.com/dotnet/runtime`

2.  **Optional: Use a GitHub Token** (for higher API rate limits or private repositories):
    ```bash
    python main.py <github_repository_url> -t <your_github_token>
    ```

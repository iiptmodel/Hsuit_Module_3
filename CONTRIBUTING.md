# Contributing

Thanks for your interest in contributing to this project! We welcome improvements, bug fixes, and documentation updates.

Guidelines
- Fork the repository and create a feature branch: `git checkout -b feature/your-feature`
- Keep changes small and focused; open one pull request per feature/bugfix
- Write or update tests for new behavior
- Ensure linters pass and code is formatted consistently

Commit messages
- Use present-tense, short summaries. Examples:
  - `fix(chat): prevent None response when summarizer returns text`
  - `feat(docs): improve quickstart and add tests instructions`

Running tests

```powershell
.\myenv\Scripts\Activate.ps1
pip install -r requirements.txt pytest
pytest -q
```

Code of conduct
- Be respectful and professional. Report toxic behavior through GitHub if necessary.

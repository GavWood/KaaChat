GOAL

> Exploration of prompts using this as a project as a base
to provide a more useful assistant

NICESITIES

Async wakewords etc.

NOTE

Current ChatGPT seems great value for a single user - but please don't rely on the token count being accurate / uptodate for enterprise.

## Install instructions for Poetry

1. Install Python3
	* assuming you know have to do this yourself
	* Windows
		* Check
			* `python --version` # Python 3.10.0 
1. Install pipx
	* https://pypa.github.io/pipx/
	* Windows:
		* `python -m pip install --user pipx`
			* will probably output a warning about the path
		* CD to the directory (e.g. c:\Users\gavin\AppData\Roaming\Python\Python310\Scripts")
		* `pipx ensurepath`
		* reload terminal
		* Check
			* `pipx --version` # 1.2.0 
1. Install Poetry
	* https://python-poetry.org/docs/#installing-with-pipx
	* `pipx install poetry`
	* Check
		* `poetry --version` # Poetry (version 1.4.1)  
1. Install dependencies
	* https://python-poetry.org/docs/basic-usage/#installing-dependencies
	* `poetry install`
	
## Install instructions for Anacodna PIP
todo

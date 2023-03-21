GOAL

> Exploration of prompts using this as a project as a base
to provide a more useful assistant

NICESITIES

Async wakewords etc.

TODO 
Lets automate the Python installation of project so John doesn't need the packages.


## Install instructions

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
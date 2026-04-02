# caasa-helper
A simple python script that exports data from caasa.it and export them in csv

> This is the first version of the script, tested only with rent and not with sale.

## Setup 

```bash
# install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# create venv with dependencies installed
uv sync
```

## Example of run 

```bash
uv run src/main.py scrape https://www.caasa.it/roma/roma/appartamento/in-affitto.html
```

## Acknowledgments

This project was developed with the assistance of AI tools, which were used for code 
generation and as learning support throughout the development process.

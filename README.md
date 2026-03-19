# caasa-helper
A simple python script that exports data from caasa.it and export them in csv

> This is the first version of the script, tested only with rent and not with sale.
> In this moment it only saves the listing names

## Setup 

```bash
python3 -m venv .venv
source .venv/bin/activate
.venv/bin/activate
pip install requirements.txt
```

## Example of run 

```bash
python3 src/main.py scrape https://www.caasa.it/roma/roma/appartamento/in-affitto.html
```

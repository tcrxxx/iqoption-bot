# IQOption BOT

## Description

Este é um projeto de estudos para criação de bots para investimento em opções binárias.

## Language

Python 3.10

## Dependencies

- ./venv/bin/pip3 install websocket-client==0.56
- ./venv/bin/pip3 install iqoptionapi
- ./venv/bin/pip3 install iqoption
- ./venv/bin/pip3 install pandas_datareader
- ./venv/bin/pip3 install matplotlib
- ./venv/bin/pip3 install pandas
- ./venv/bin/pip3 install numpy
- ./venv/bin/pip3 install pushbullet.py

## How to use

1) Create config.py
2) Into config.py create IQOPTION_USER, IQOPTION_PASS and PUSHBULLET_API_TOKEN, like:
```python
IQOPTION_USER='myuser@gmail.com'
IQOPTION_PASS='mypassword'

PUSHBULLET_API_TOKEN='mytoken'
```

## How to run

```shell
{yout_project_path}/venv/bin/python {yout_project_path}/iqoption-bot/main.py

```
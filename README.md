# naivete

Robinhood Trading Bot based on a simple naive idea

Forked from https://github.com/2018kguo/RobinhoodBot

## Requirements

Python 3.9+

## Naive Algorithm

* Buy stock at X-week low, but delay until stock has recovered by 0.5%
* Sell stock at X-week high, but delay until stock has dropped by 0.5%

## Installation

```bash
pip install -r requirements.txt
cp config.py.sample config.py # add auth info after copying
```

## Running

```python
python3 main.py
```
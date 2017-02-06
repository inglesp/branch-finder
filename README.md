# Branch finder

This repo contains a Python script, `find_branches.py`, that helps you find supermarket branches near a given location.

## Setup

Run

    $ pip install -r requirements.txt

to install the script's dependencies.

## Usage

Run

    $ python find_branches.py

for usage instructions.

For instance, to find branches of Tesco within one mile of 10 Downing Street, run

    $ python find_branches.py --chain=tesco --within-distance-miles=1 --address="10 Downing Street London"

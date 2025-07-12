#!/bin/bash

source .venv/bin/activate

set -a
source app/prod.env
set +a

python3 app/pddl_generator_agent.py
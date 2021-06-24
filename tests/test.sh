#!/bin/bash

set -e 
set -o pipefail

pytest tests/doc

for entry in "tests/examples/test_"*
do
  # Tests have to run separately bc of the NEURON package linking
  echo "Testing $entry"
  pytest $entry
done

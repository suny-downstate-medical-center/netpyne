#!/bin/bash

set -e 
set -o pipefail

for entry in tests/*/test_*
do
  # Tests have to run separately bc of the NEURON package linking
  echo "Testing $entry"
  pytest $entry
done

#!/bin/bash
set -u
mkdir -p /logs/verifier
python3 /tests/verify.py
if [ ! -f /logs/verifier/reward.json ]; then
  echo '{"overall": 0.0}' > /logs/verifier/reward.json
fi
exit 0

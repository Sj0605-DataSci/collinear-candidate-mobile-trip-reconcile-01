#!/bin/bash
# Oracle solution: a literal recorded human interaction script -- real
# tap/swipe/type/home/back calls through the SAME tool scripts the agent
# uses (not a database shortcut), replaying exactly how a person would
# actually use their phone to do this: check Calendar, check Chat, open
# TripDesk in Chrome, search/select flight+hotel, wait for and notice the
# mid-mission update, re-check Chat, correct the plan, confirm. See
# oracle_steps.py for the actual coordinate sequence (determined by
# interactively exploring this exact built image -- see RUN_REPORT.md).
set -eu
python3 /solution/oracle_steps.py

#!/usr/bin/env bash
set -euxo pipefail

OPERATE_ON="Octoprint_Smart_Pow/octoprint_smart_pow"

python -m black --line-length 81 $OPERATE_ON

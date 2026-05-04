#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$SCRIPT_DIR"
while [[ "$ROOT" != "/" ]]; do
  if [[ -f "$ROOT/automation/oph_completion/oracle_task_pipeline.py" ]]; then
    break
  fi
  ROOT="$(dirname "$ROOT")"
done

if [[ ! -f "$ROOT/automation/oph_completion/oracle_task_pipeline.py" ]]; then
  echo "Could not find automation/oph_completion/oracle_task_pipeline.py above $SCRIPT_DIR" >&2
  exit 1
fi

cd "$ROOT"

CAMPAIGN_REL="reverse-engineering-reality/code/particles/campaigns/gap_bundle"

python3 automation/oph_completion/oracle_task_pipeline.py \
  --task-tree "$CAMPAIGN_REL/task_tree.json" \
  --state "$CAMPAIGN_REL/state.json" \
  --runs-dir "$CAMPAIGN_REL/runs" \
  --threads-dir "$CAMPAIGN_REL/threads" \
  run-ready \
  --config "$CAMPAIGN_REL/pipeline_config.json" \
  "$@"

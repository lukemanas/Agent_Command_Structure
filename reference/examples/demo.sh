#!/usr/bin/env bash
# demo.sh — walk the protocol end-to-end, including expected rejections.
#
# Run from this directory:
#   bash demo.sh
#
# Uses an isolated AGENTCS_HOME so it doesn't touch your real ~/.agentcs/.
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
AGENTCS="python3 ${HERE}/../agentcs.py"

export AGENTCS_HOME="${HERE}/.agentcs-demo"
rm -rf "${AGENTCS_HOME}"

step() { echo; echo "▌ $*"; }
expect_reject() {
  echo "  (expecting REJECTED)"
  if "$@"; then
    echo "  ✗ expected reject but command succeeded"
    exit 1
  else
    echo "  ✓ rejected as expected"
  fi
}

step "1. human initiates project from SOW"
$AGENTCS init --from-file "${HERE}/sow.json"
$AGENTCS status

step "2. planner proposes OAP"
AGENTCS_AS=planning-1 $AGENTCS propose-oap --from-file "${HERE}/oap.json"

step "3. human approves OAP → CoS spawns (status: spawned, not active)"
$AGENTCS approve-oap
$AGENTCS status

step "4. cos-1 tries to create issues BEFORE checkin (must reject)"
expect_reject env AGENTCS_AS=cos-1 $AGENTCS create-issues

step "5. cos-1 attempts checkin with WRONG period (must reject)"
expect_reject env AGENTCS_AS=cos-1 $AGENTCS checkin --role cos --period 99 --risk low

step "6. cos-1 attempts checkin with WRONG role (must reject)"
expect_reject env AGENTCS_AS=cos-1 $AGENTCS checkin --role worker --period 1 --risk low

step "7. cos-1 checks in correctly"
AGENTCS_AS=cos-1 $AGENTCS checkin --role cos --period 1 --risk low

step "8. cos-1 spawns worker-1 and creates issues from OAP"
AGENTCS_AS=cos-1 $AGENTCS spawn worker-1 --role worker --skill worker
AGENTCS_AS=cos-1 $AGENTCS create-issues

step "9. worker-1 tries to act before checkin (must reject)"
expect_reject env AGENTCS_AS=worker-1 $AGENTCS transition issue-obj-1 in-progress

step "10. worker-1 checks in"
AGENTCS_AS=worker-1 $AGENTCS checkin --role worker --period 1 --risk low --objectives obj-1,obj-2

step "11. anyone tries to expand scope (must reject — the protocol invariant)"
expect_reject $AGENTCS scope add obj-99 --reason "I think we should add this"

step "12. worker-1 progresses obj-1 through the lifecycle"
AGENTCS_AS=worker-1 $AGENTCS transition issue-obj-1 in-progress
AGENTCS_AS=worker-1 $AGENTCS transition issue-obj-1 ready-for-review
echo "  ✓ note: worker did NOT record verification yet"

step "13. cos-1 moves to pending-review"
AGENTCS_AS=cos-1 $AGENTCS transition issue-obj-1 pending-review

step "14. cos-1 tries to close WITHOUT verification (must reject — verified-before-close)"
expect_reject env AGENTCS_AS=cos-1 $AGENTCS transition issue-obj-1 closed

step "15. worker-1 records verification, cos-1 closes"
AGENTCS_AS=worker-1 $AGENTCS verify issue-obj-1 "pytest tests/test_hello.py — 1 passed"
AGENTCS_AS=cos-1 $AGENTCS transition issue-obj-1 closed

step "16. obj-2: human reduces scope mid-OP (allowed)"
$AGENTCS scope reduce obj-2 --reason "out of time; deferring test to next OP"

step "17. cos-1 proposes ARR"
AGENTCS_AS=cos-1 $AGENTCS propose-arr

step "18. human reviews ARR"
$AGENTCS review-arr accept --comment "obj-1 verified; obj-2 deferred per scope reduction"

step "19. human demobilizes — sandbox destroyed, registry cleared"
$AGENTCS demob

step "20. final audit log (project demobilized; logs persist)"
$AGENTCS audit --project demo-001

echo
echo "▌ DONE — protocol lifecycle exercised end-to-end."

#!/usr/bin/env bash
# Cloud (vast.ai) setup for the M9 corpus mass runs — adapted from the
# maintainer's setup_thesis_b2.sh orchestrator.
#
# SECURITY: credentials come from the environment, NEVER from this file and
# NEVER from the bundle. Before running, export:
#   export B2_ACCOUNT=...   # B2 applicationKeyId (use a bucket-scoped key)
#   export B2_KEY=...       # B2 applicationKey
#   export B2_BUCKET=...    # bucket name
#
# What it does:
#   1. installs + configures rclone from the env vars
#   2. resumably downloads the split bundle (bench_bundle.tar.gz.part.*),
#      merges, extracts into ./project
#   3. builds the main venv (Qwen/GLM/Kimi lanes); optionally the isolated
#      DeepSeek-VL2 venv (SETUP_DEEPSEEK=1)
#   4. starts cron + a ledger monitor that sync data/runs -> B2 every cycle
#      (the JSONL ledgers are the only irreplaceable output; runs are
#      record-atomically resumable from them after any preemption)
#   5. prints the shard commands — it does NOT start GPU work itself
set -euo pipefail

: "${B2_ACCOUNT:?export B2_ACCOUNT (B2 applicationKeyId) first}"
: "${B2_KEY:?export B2_KEY (B2 applicationKey) first}"
: "${B2_BUCKET:?export B2_BUCKET (bucket name) first}"
SETUP_DEEPSEEK="${SETUP_DEEPSEEK:-0}"
SETUP_KIMI="${SETUP_KIMI:-0}"

REMOTE_NAME="b2bench"
WORKDIR="$(pwd)"
PROJECT_DIR="$WORKDIR/project"
RUNS_DIR="$PROJECT_DIR/data/runs"
PART_PATTERN="bench_bundle.tar.gz.part.*"
ARCHIVE_NAME="bench_bundle.tar.gz"
LOG_DIR="$WORKDIR/logs"
CRON_LOG="$LOG_DIR/cron.log"
MONITOR_LOG="$LOG_DIR/ledger_monitor.log"

GREEN="\033[1;32m"; RED="\033[1;31m"; CYAN="\033[1;36m"; RESET="\033[0m"
info()    { echo -e "${CYAN}i  $1${RESET}"; }
success() { echo -e "${GREEN}ok $1${RESET}"; }
fail()    { echo -e "${RED}xx $1${RESET}"; exit 1; }

# Interrupt trap: the ledgers are the run — push them before dying.
trap 'echo "interrupt — emergency ledger sync";
      rclone copy "$RUNS_DIR" "$REMOTE_NAME:$B2_BUCKET/bench_runs_interrupt_$(date +%F_%H-%M)" || true' \
      SIGINT SIGTERM

mkdir -p "$LOG_DIR"

# ---- rclone install + config (creds from env only) ----
if ! command -v rclone >/dev/null 2>&1; then
    info "installing rclone..."
    (sudo apt-get update && sudo apt-get install -y rclone) \
        || curl -fsSL https://rclone.org/install.sh | sudo bash
fi
mkdir -p "$HOME/.config/rclone"
cat >"$HOME/.config/rclone/rclone.conf" <<EOF
[$REMOTE_NAME]
type = b2
account = $B2_ACCOUNT
key = $B2_KEY
EOF
chmod 600 "$HOME/.config/rclone/rclone.conf"
rclone lsf "$REMOTE_NAME:$B2_BUCKET" >/dev/null 2>&1 \
    || fail "cannot list $REMOTE_NAME:$B2_BUCKET — check credentials/scoping"
success "B2 remote configured and reachable"

# ---- resumable bundle download + verify + merge + extract ----
# The bundle lives under the bucket's bench/ prefix (with BUNDLE_SHA256SUMS).
info "downloading bundle parts ($PART_PATTERN) from $B2_BUCKET/bench ..."
rclone copy "$REMOTE_NAME:$B2_BUCKET/bench" "$WORKDIR" --progress
shopt -s nullglob
PARTS=($PART_PATTERN)
shopt -u nullglob
[[ "${#PARTS[@]}" -gt 0 ]] || fail "no bundle parts found under $B2_BUCKET/bench"
success "downloaded ${#PARTS[@]} parts"

info "verifying checksums ..."
sha256sum -c BUNDLE_SHA256SUMS --ignore-missing || fail "bundle checksum mismatch"

info "merging + extracting into $PROJECT_DIR ..."
cat "${PARTS[@]}" > "$ARCHIVE_NAME"
mkdir -p "$PROJECT_DIR"
tar --no-same-owner -xzf "$ARCHIVE_NAME" -C "$PROJECT_DIR"
rm -f "${PARTS[@]}" "$ARCHIVE_NAME"
[[ -f "$PROJECT_DIR/scripts_run_shard.py" ]] \
    || fail "bundle layout unexpected: scripts_run_shard.py not at project root"
success "bundle extracted"

# ---- main venv (Qwen / GLM / Kimi lanes) ----
cd "$PROJECT_DIR"
info "building main venv..."
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip -q
pip install -e ".[pipeline]" -q
# Rental images often run older drivers than the newest torch wheels
# require; fall back to cu126 builds instead of failing the whole setup.
if ! python -c "import torch; assert torch.cuda.is_available()" 2>/dev/null; then
    info "default torch wheels reject this driver — falling back to cu126 wheels..."
    pip install -q --force-reinstall torch torchvision \
        --index-url https://download.pytorch.org/whl/cu126
fi
python -c "import torch; assert torch.cuda.is_available(), 'no CUDA'; print('CUDA ok:', torch.cuda.get_device_name(0))"
deactivate
success "main venv ready"

# ---- optional isolated DeepSeek-VL2 venv ----
if [[ "$SETUP_DEEPSEEK" == "1" ]]; then
    info "building isolated DeepSeek-VL2 venv (.venv-dsvl2)..."
    # torch 2.0.1 (deepseek_vl2's exact pin) ships no wheels for
    # Python >= 3.12; provision CPython 3.10 via uv when needed.
    PYMINOR=$(python3 -c 'import sys; print(sys.version_info.minor)')
    if [[ "$PYMINOR" -ge 12 ]]; then
        command -v uv >/dev/null || curl -LsSf https://astral.sh/uv/install.sh | sh
        export PATH="$HOME/.local/bin:$PATH"
        uv venv --python 3.10 --seed .venv-dsvl2
    else
        python3 -m venv .venv-dsvl2
    fi
    source .venv-dsvl2/bin/activate
    pip install --upgrade pip -q
    pip install -r config/env_deepseek_vl2_requirements.txt -q
    # adapter deps the package does not declare (also in newer req files;
    # explicit here because the bundle may carry an older copy): numpy must
    # stay 1.x for the torch 2.0.1-era stack.
    pip install "numpy<2" pillow -q
    # attrdict (transitive dep) is import-broken on Python >= 3.10; replace
    # with the maintained fork AFTER install (both ship the same module).
    pip uninstall -y attrdict -q || true
    pip install attrdict3 -q
    pip install -e . --no-deps -q   # benchmark package only; deps come from the spec file
    python -c "import deepseek_vl2, attrdict; print('deepseek_vl2 import ok')"
    pip freeze > "$RUNS_DIR/../env_dsvl2_freeze.txt" || true
    deactivate
    success "DeepSeek venv ready (freeze recorded)"
fi

# ---- optional isolated Kimi-VL venv (backup lane; transformers 4.x pin) ----
if [[ "$SETUP_KIMI" == "1" ]]; then
    info "building isolated Kimi-VL venv (.venv-kimi)..."
    python3 -m venv .venv-kimi
    source .venv-kimi/bin/activate
    pip install --upgrade pip -q
    pip install -r config/env_kimi_vl_requirements.txt -q
    pip install -e . --no-deps -q
    pip freeze > "$RUNS_DIR/../env_kimi_freeze.txt" || true
    deactivate
    success "Kimi venv ready (freeze recorded)"
fi

# ---- ledger backups: cron every 15 min + change-triggered monitor ----
mkdir -p "$RUNS_DIR"
rclone copy "$RUNS_DIR" "$REMOTE_NAME:$B2_BUCKET/bench_runs_auto" --progress || true
CRON_JOB="*/15 * * * * rclone copy $RUNS_DIR $REMOTE_NAME:$B2_BUCKET/bench_runs_auto >> $CRON_LOG 2>&1"
EXISTING_CRON="$(crontab -l 2>/dev/null || true)"
if ! echo "$EXISTING_CRON" | grep -Fq "$RUNS_DIR $REMOTE_NAME:$B2_BUCKET/bench_runs_auto"; then
    (echo "$EXISTING_CRON"; echo "$CRON_JOB") | crontab -
fi
success "cron ledger backup installed (every 15 min)"

(
    last_state=""
    while true; do
        state="$(find "$RUNS_DIR" -type f -name '*.jsonl' -printf '%T@ %s\n' 2>/dev/null | sort | md5sum)"
        if [[ -n "$state" && "$state" != "$last_state" ]]; then
            rclone copy "$RUNS_DIR" "$REMOTE_NAME:$B2_BUCKET/bench_runs_auto" \
                --log-file="$MONITOR_LOG" --log-level INFO \
                || echo "[$(date)] sync failed" >> "$MONITOR_LOG"
            last_state="$state"
        fi
        sleep 300
    done
) &
success "ledger monitor started"

# ---- done: print (do not start) the shard commands ----
success "setup complete — GPU work is NOT auto-started."
cat <<'EOF'

FIRST: run the registered CAL-50 gate once per generator-contract in this
environment (prereg-m9-v1; shards refuse to start without a passing
artifact for the exact identity):

  source .venv/bin/activate
  python scripts_run_shard.py --generator qwen --run-gate
  python scripts_run_shard.py --generator glm  --run-gate

Then run shards (each is resume-capable; rerun the same command after any
preemption and it continues from the last committed record):

  python scripts_run_shard.py --generator qwen --shard-start 0     --shard-end 4549
  python scripts_run_shard.py --generator glm  --shard-start 0     --shard-end 4549
  ...

Thinking-mode ablation lane (registered subset, positions 0-1999; runs
AFTER corpus lanes; outputs never enter corpus labels):

  python scripts_run_shard.py --generator glm-thinking --run-gate
  python scripts_run_shard.py --generator glm-thinking --shard-start 0 --shard-end 2000

DeepSeek lane (only with SETUP_DEEPSEEK=1 at setup):

  source .venv-dsvl2/bin/activate
  python scripts_run_shard.py --generator deepseek --shard-start 0 --shard-end 4549

Kimi backup lane (only with SETUP_KIMI=1; recorded substitution only):

  source .venv-kimi/bin/activate
  python scripts_run_shard.py --generator kimi --shard-start 0 --shard-end 4549

Ledgers under data/runs/ sync to B2 automatically (cron + monitor).
EOF

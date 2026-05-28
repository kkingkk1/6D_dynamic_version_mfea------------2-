#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

JAVA_BIN="${JAVA_BIN:-java}"
MVN_BIN="${MVN_BIN:-mvn}"
BASE_TUNING_CONFIG="${BASE_TUNING_CONFIG:-tuning.properties}"
RESULT_ROOT="${RESULT_ROOT:-$SCRIPT_DIR/result}"
SCENE_ROOT="${SCENE_ROOT:-E:/OneDrive/project/paper_reproduction/AutoHyb/Code4mfea_mophoa_2/Code4mfea_mophoa_java_satellite_scheduling/Scene}"
ROUNDS="${ROUNDS:-1}"
START_ROUND="${START_ROUND:-1}"
N_RUN="${N_RUN:-1}"
N_POP="${N_POP:-}"
MAX_FES="${MAX_FES:-}"
POPULATION_FACTOR="${POPULATION_FACTOR:-}"
SKIP_COMPILE="${SKIP_COMPILE:-false}"
HYBRID_CONFIG="${HYBRID_CONFIG:-4,1,0,0,0,0}"

PATH_SEP=':'
case "$(uname -s 2>/dev/null || echo unknown)" in
  CYGWIN*|MINGW*|MSYS*) PATH_SEP=';' ;;
esac
CP="target/classes${PATH_SEP}target/test-classes"
MAIN_CLASS="main.RunSingleHybridConfig"

timestamp="$(date +%Y%m%d_%H%M%S)"
out_dir="$RESULT_ROOT/benchmark_fixed_topk_135_${timestamp}"
log_dir="$out_dir/logs"
config_dir="$out_dir/configs"
mkdir -p "$log_dir" "$config_dir"
csv_file="$out_dir/fixed_topk_raw.csv"
summary_file="$out_dir/fixed_topk_summary.csv"

base_config="$config_dir/default_ranker.properties"
fixed_topk_config="$config_dir/fixed_topk.properties"
cp "$BASE_TUNING_CONFIG" "$base_config"
cp "$BASE_TUNING_CONFIG" "$fixed_topk_config"
{
  echo
  echo "# fixed-topk override"
  echo "ranker.ordinaryTopK=2"
  echo "ranker.prioritizedTopK=4"
} >> "$fixed_topk_config"

scenarios=(
  "1|500-5-0-0-24|500|5|$SCENE_ROOT/500-5-0-0-24"
  "3|1000-10-0-0-12|1000|10|$SCENE_ROOT/1000-10-0-0-12"
  "5|1000-20-0-0-12|1000|20|$SCENE_ROOT/1000-20-0-0-12"
)

variants=(
  "default_ranker|baseline|$base_config"
  "fixed_topk|fixed-topk|$fixed_topk_config"
)

parse_profit_ratio() {
  awk -F': ' '/Optimized profit ratio:/ { gsub(/%/, "", $2); print $2; exit }' "$1"
}

parse_elapsed_seconds() {
  awk -F': ' '/Elapsed:/ { gsub(/ s/, "", $2); print $2; exit }' "$1"
}

run_case() {
  local scene_id="$1"
  local scenario_name="$2"
  local num_tasks="$3"
  local num_satellites="$4"
  local data_dir="$5"
  local variant_name="$6"
  local variant_label="$7"
  local config_path="$8"
  local round_idx="$9"
  local log_file="$log_dir/scene${scene_id}_${scenario_name}_${variant_name}_round${round_idx}.log"

  if [[ ! -d "$data_dir" ]]; then
    echo "[error] missing scenario directory: $data_dir" >&2
    return 1
  fi

  "$JAVA_BIN" \
    "-Dtuning.config.path=$config_path" \
    "-Devaluation.runIndexBase=$((round_idx - 1))" \
    -cp "$CP" "$MAIN_CLASS" \
    true true "$data_dir" "$num_tasks" "$num_satellites" "$HYBRID_CONFIG" "$N_RUN" "$N_POP" "$MAX_FES" "$POPULATION_FACTOR" \
    >"$log_file" 2>&1

  local profit_ratio elapsed_seconds
  profit_ratio="$(parse_profit_ratio "$log_file")"
  elapsed_seconds="$(parse_elapsed_seconds "$log_file")"
  if [[ -z "$profit_ratio" || -z "$elapsed_seconds" ]]; then
    echo "[error] failed to parse result: $log_file" >&2
    tail -n 60 "$log_file" >&2
    return 1
  fi

  printf '%s,%s,%s,%s,%s,%s,%s,%s,%s,%s\n' \
    "$scene_id" "$scenario_name" "$num_tasks" "$num_satellites" "$variant_name" "$variant_label" "$round_idx" \
    "$profit_ratio" "$elapsed_seconds" "$log_file" >> "$csv_file"

  printf '  scene=%s %-18s %-26s round=%-2s profit_ratio=%8s%% elapsed=%8ss\n' \
    "$scene_id" "$scenario_name" "$variant_name" "$round_idx" "$profit_ratio" "$elapsed_seconds"
}

if [[ "$SKIP_COMPILE" != "true" ]]; then
  echo "[fixed-topk] compiling project..."
  "$MVN_BIN" -f "$SCRIPT_DIR/pom.xml" -q -DskipTests compile
fi

echo "scene_id,scenario,num_tasks,num_satellites,variant,variant_label,round,profit_ratio,elapsed_seconds,log_file" > "$csv_file"
echo "[fixed-topk] output: $out_dir"
last_round=$((START_ROUND + ROUNDS - 1))
echo "[fixed-topk] scenes=1,3,5, variants=baseline/fixed-topk, rounds=${START_ROUND}-${last_round}, nRun=$N_RUN"

for scenario in "${scenarios[@]}"; do
  IFS='|' read -r scene_id scenario_name num_tasks num_satellites data_dir <<< "$scenario"
  for variant in "${variants[@]}"; do
    IFS='|' read -r variant_name variant_label config_path <<< "$variant"
    for ((round_idx=START_ROUND; round_idx<=last_round; round_idx++)); do
      run_case "$scene_id" "$scenario_name" "$num_tasks" "$num_satellites" "$data_dir" "$variant_name" "$variant_label" "$config_path" "$round_idx"
    done
  done
done

summary_body="$out_dir/summary_body.tmp"
awk -F',' '
  NR > 1 {
    key = $1 "," $2 "," $3 "," $4 "," $5 "," $6
    sum_profit_ratio[key] += $8
    sum_elapsed[key] += $9
    count[key] += 1
  }
  END {
    for (key in count) {
      printf "%s,%d,%.4f,%.4f\n",
        key, count[key],
        sum_profit_ratio[key] / count[key],
        sum_elapsed[key] / count[key]
    }
  }
' "$csv_file" | sort -t',' -k1,1n -k5,5 > "$summary_body"
{
  echo "scene_id,scenario,num_tasks,num_satellites,variant,variant_label,rounds,avg_profit_ratio,avg_elapsed_seconds"
  cat "$summary_body"
} > "$summary_file"
rm -f "$summary_body"

echo "[fixed-topk] summary:"
cat "$summary_file"
echo "[fixed-topk] raw csv: $csv_file"

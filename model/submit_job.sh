#!/bin/sh
python=$HOME/miniconda3/envs/tf/bin/python3

# get run info
output_dir="save"
run_name=$($python -B -c "import run_opts; print(run_opts.config_runtime['run_name'])")
list=$($python -B -c "import run_opts; print(run_opts.config_runtime['dataset'])")

## clear existing directory
if [ -d "$output_dir/$run_name" ]; then
    echo "Removing previous session: $output_dir/$run_name"
    rm -rf "$output_dir/$run_name"
fi

# create save directories
mkdir -p "$output_dir/$run_name"

## copy source files
cp *.py "$output_dir/$run_name"
cp -L -r src "$output_dir/$run_name"
cp "$list" "$output_dir/$run_name"

## copy job file
cp train.sh "$output_dir/$run_name"

# go to working directory
cd "$output_dir/$run_name"

# debug print
echo "Working directory: $(pwd)"
## queue job
bash train.sh "$list"

cd ../../
echo "Training started"
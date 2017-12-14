
export BASE_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )/../../.." && pwd )"
export PYTHONPATH=$PYTHONPATH:$BASE_DIR/code/RMG-Py
export PYTHONPATH=$PYTHONPATH:$BASE_DIR/code/autoQM
export PATH=$BASE_DIR/anaconda/bin:$PATH
# some might use miniconda
# uncomment the line below if so
# export PATH=$BASE_DIR/miniconda/bin:$PATH

source activate autoqm_env

echo $(date +%Y-%m-%d:%H:%M:%S) 
echo "autoQM directory: "$BASE_DIR/code/autoQM
python $BASE_DIR/code/autoQM/autoqm/archiver.py

source deactivate
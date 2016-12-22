#!/bin/bash
TMP="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TMP="$( dirname $TMP)"
export PE_PATH=$TMP/pe
export PYTHONPATH=$PE_PATH
echo $PE_PATH
python $PE_PATH/pe_update_token.py -t $PE_PATH/.token
export PE_N_OF_SOLVED_FILE=pe.out.N_of_solved.txt
export PE_SESSID_FILE=__pesessid.txt
echo 0 > $PE_N_OF_SOLVED_FILE

python $* | tee pe.out.log.txt


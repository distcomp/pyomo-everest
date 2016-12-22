set PE_PATH=<path to pyomo_everest folder>
set PYTHONPATH=%PE_PATH%
echo %PE_PATH%
python %PE_PATH%\pe_update_token.py -t %PE_PATH%\.token
set PE_N_OF_SOLVED_FILE=pe.out.N_of_solved.txt
set PE_SESSID_FILE=__pesessid.txt
echo 0 > %PE_N_OF_SOLVED_FILE%

python %1 %2 %3 %4 %5 %6 %7 %8 %9 2> %1.err.log.txt


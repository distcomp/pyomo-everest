set PE_DIR=C:\pyomo\pyomoeverest
set PYTHONPATH=%PE_DIR%
echo %PE_DIR%
python %PE_DIR%\pe_update_token.py -t %PE_DIR%\.token
set PE_N_OF_SOLVED_FILE=pe.out.N_of_solved.txt
set PE_SESSID_FILE=__pesessid.txt
echo 0 > %PE_N_OF_SOLVED_FILE%

python %1 %2 %3 %4 %5 %6 %7 %8 %9 2> %1.err.log.txt


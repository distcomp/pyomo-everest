RESOURCES = [
    "52eb8d4e420000f401166a2e", # irbis1
    "544e54293300003f0038c674", # restopt-vm1
    "544e82673300003f0038c687", # restopt-vm2
    "578ea88d310000b33c8c7f44"  # fujiRestOpt
]

SSOP_RESOURCES = {"vvvolhome"      : "5d167bbf1200008937f93ff9", \
                  "vvvolhome2"     : "5e33cf6211000075006a321f", \
                  "vvvoldell"      : "5c5b0d9c410000a25e4c9b99", \
                  "ui4.kiae.vvvol" : "5addfc3115000084cb623517", \
                  "hse"            : "5e3ec8641100003a446a8be5"  \
                  }
                  # "ui4.kiae"     : "59c520773300004852f4363a", \
                  # "govorun"      : "5d44926b0f0000b553cd4172" \

                  # 'irbis1'       : '52eb8d4e420000f401166a2e', \
                  # 'fujiRestOpt'  : '578ea88d310000b33c8c7f44', \
                  # 'restopt-vm1'  : '544e54293300003f0038c674', \
                  # 'restopt-vm2'  : '544e82673300003f0038c687', \

# Solvers available for SSOP
SSOP_SOLVERS = ["ipopt", "scip"]
SOLVER_OPTIONS_DELIMETER = {"ipopt" : " ", "scip" : " = "}

PARAMETER_SWEEP_ID = "530f36d73d00002d04548b0e"
SOLVE_AMPL_STUB_ID = "vladimirv/solve-ampl-stub" #"531f44233e0000c015f09ad3"
SSOP_ID = "vladimirv/solve-set-opt-probs" #"5bb2783e420000772e1049fd"


# Add your Everest login and password here to make token update automatically
SSOP_TOKEN_FILE = "/home/vladimirv/mc2/python-api/.token30d" #"/home/vladimirv/python_work/pyomo-everest/ssop/.token" #" "C:\\_SvF\\TMP\\.token"
UPDATE_TOKEN_PERIOD_IN_SEC = 7*24*3600 - 5*3600

# Working dirs
SSOP_DEFAULT_WORKING_DIR = "/home/vladimirv/python_work/pyomo-everest/ssop/.tmp"

# Run miscellaneous
SSOP_RUN_SH_PREFIX = "run-" # run-ipopt.sh, run-scip.sh, run-fscip.sh ...

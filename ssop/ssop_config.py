RESOURCES = [
    '52eb8d4e420000f401166a2e', # irbis1
    '544e54293300003f0038c674', # restopt-vm1
    '544e82673300003f0038c687', # restopt-vm2
    '578ea88d310000b33c8c7f44'  # fujiRestOpt
]

SSOP_RESOURCES = {'irbis1':'52eb8d4e420000f401166a2e', \
                  'fujiRestOpt':'578ea88d310000b33c8c7f44', \
                  'restopt-vm1':'544e54293300003f0038c674', \
                  'restopt-vm2': '544e82673300003f0038c687'}

PARAMETER_SWEEP_ID = '530f36d73d00002d04548b0e'
SOLVE_AMPL_STUB_ID = '531f44233e0000c015f09ad3'
SSOP_ID = '5bb2783e420000772e1049fd'


# Add your Everest login and password here to make token update automatically
SSOP_TOKEN_FILE = '.ssop_token'
UPDATE_TOKEN_PERIOD_IN_SEC = 7*24*3600 - 5*3600
EVEREST_LOGIN = None  #'YOUR_EVEREST_USER_LOGIN'
EVEREST_PASSW = None  #'YOUR_EVEREST_PASSWORD'

# Working dirs
SSOP_DEFAULT_WORKING_DIR = 'ssop.tmp'

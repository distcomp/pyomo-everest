#TMP="$( dirname "${BASH_SOURCE[0]}" )"
TMP="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TMP="$( dirname $TMP)"
PE_PATH=$TMP/pe
echo $PE_PATH
exit 0
TMP="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
echo $TMP
cd $TMP
cd ../pe

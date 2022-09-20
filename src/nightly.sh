#!/bin/bash

set -x
set -e

SCRIPT_DIR=$(dirname "${0}")
SCRIPT_LOCATION=$(readlink -f "${SCRIPT_DIR}")

check_date=$(date +%s)
GIT_LOCATION=$(cd "${SCRIPT_LOCATION}" && cd .. && pwd)
NIGHTLIES_LOCATION=${GIT_LOCATION}/nightlies
THIS_NIGHTLY_LOCATION=${NIGHTLIES_LOCATION}/${check_date}

mkdir -p "${NIGHTLIES_LOCATION}"
mkdir "${THIS_NIGHTLY_LOCATION}"

# Make temporary splash page for two nightlies
cd "${THIS_NIGHTLY_LOCATION}"
cat <<EOF >index.html
<!doctype html>
<meta charset="utf-8" />
<title>Megalibm Results for $(date +%Y-%m-%d)</title>
<h1>TEMPORARY SPLIT NIGHTLY</h1>
<a href="identities.html">Identity generation nightly</a><br>
<a href="generated/index.html">Function generation nightly</a>
EOF

# Run the identities nightly
/usr/bin/time -v "${SCRIPT_LOCATION}"/megalibm_identities "${GIT_LOCATION}/benchmarks/"

# Run the generation nightly, this is more envolved
/usr/bin/time -v "${SCRIPT_LOCATION}"/megalibm_generate "${GIT_LOCATION}/benchmarks/"

rm -rf "${GIT_LOCATION}/measurement/error/generated"
mv "${THIS_NIGHTLY_LOCATION}/generated/" "${GIT_LOCATION}/measurement/error/"
cd "${GIT_LOCATION}/measurement/error/"
make -j6 build
make -j6 run
./scripts/plot_error.py generated
mv generated "${THIS_NIGHTLY_LOCATION}"

# Gather output files

if [ "$(hostname)" = "warfa" ] && [ "${USER}" != "ibriggs" ]; then
    scp -r "${THIS_NIGHTLY_LOCATION}" uwplse.org:/var/www/megalibm/
fi

if command -v nightly-results &>/dev/null; then
    nightly-results url https://megalibm.uwplse.org/"${check_date}/"
fi

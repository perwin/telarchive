#! /bin/bash
#
# Script for running regression tests for telarchive; should ideally be
# run from within the telarchive directory.
# 
# Note that we run with threading turned off so that all searches
# run in the same order.

# We assume that the reference output are in a *local* directory called
# "testing"
TELARCHIVE="./archive_search.py"
TESTDATA_DIR="testing"
FAILED_TEXT=" ** Test failed. **"

echo -e "\nRunning regression tests for telarchive\n"

# test for a good object search:
echo "Running NGC 936 search..."
${TELARCHIVE} --nothreads "ngc 936" > regresstest_out1.txt
echo -n "Comparing text output with reference... "
if (diff --brief regresstest_out1.txt ${TESTDATA_DIR}/search_n936_output.txt)
then
  echo " OK"
else
  echo "${FAILED_TEXT}"
fi

# test for another good object search (more hits):
echo "Running NGC 4321 search..."
${TELARCHIVE} --nothreads "ngc 4321" > regresstest_out2.txt
echo -n "Comparing text output with reference... "
if (diff --brief regresstest_out2.txt ${TESTDATA_DIR}/search_n4321_output.txt)
then
  echo " OK"
else
  echo "${FAILED_TEXT}"
fi

# test for a good southern object search (more hits):
echo "Running NGC 1399 search..."
${TELARCHIVE} --nothreads "ngc 1399" > regresstest_out3.txt
echo -n "Comparing text output with reference... "
if (diff --brief regresstest_out3.txt ${TESTDATA_DIR}/search_n1399_output.txt)
then
  echo " OK"
else
  echo "${FAILED_TEXT}"
fi

# test for bad object name:
echo "Running bad-object-name search..."
${TELARCHIVE} --nosdss --nothreads "ngc bob" > regresstest_out4.txt
echo -n "Comparing text output with reference... "
if (diff --brief regresstest_out4.txt ${TESTDATA_DIR}/search_ngcbob_output.txt)
then
  echo " OK"
else
  echo "${FAILED_TEXT}"
fi

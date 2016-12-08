##
## Tests for SANS
##

set ( TEST_PY_FILES
  command_interface_state_director_test.py
)

check_tests_valid ( ${CMAKE_CURRENT_SOURCE_DIR} ${TEST_PY_FILES} )

# Prefix for test name=PythonAlgorithms
pyunittest_add_test ( ${CMAKE_CURRENT_SOURCE_DIR} PythonAlgorithmsSANS ${TEST_PY_FILES} )

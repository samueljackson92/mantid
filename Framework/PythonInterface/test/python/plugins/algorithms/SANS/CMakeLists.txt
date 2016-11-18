######################
# Tests for ISIS SANS
######################

set ( TEST_PY_FILES
MergeReductionsTest.py
SANSCalculateTransmissionTest.py
SANSConvertToQTest.py
SANSConvertToWavelengthTest.py
SANSCreateAdjustmentWorkspacesTest.py
SANSCreateWavelengthAndPixelAdjustmentTest.py
SANSNormalizeToMonitorTest.py
SANSScaleTest.py
SANSSliceEventTest.py
StripEndNansTest.py
)

check_tests_valid ( ${CMAKE_CURRENT_SOURCE_DIR} ${TEST_PY_FILES} )

# Prefix for test name=PythonAlgorithms_SANS
pyunittest_add_test ( ${CMAKE_CURRENT_SOURCE_DIR} PythonAlgorithms ${TEST_PY_FILES} )

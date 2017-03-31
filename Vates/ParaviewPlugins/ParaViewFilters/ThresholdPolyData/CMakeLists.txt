PROJECT(ThresholdPolyData)
include_directories( SYSTEM ${PARAVIEW_INCLUDE_DIRS} )
ADD_PARAVIEW_PLUGIN(MantidParaViewThresholdPolyDataSMPlugin "1.0"
SERVER_MANAGER_XML ThresholdPolyData.xml
SERVER_MANAGER_SOURCES vtkThresholdPolyData.cxx)
# Add to the 'VatesParaViewPlugins' group in VS
set_property( TARGET MantidParaViewThresholdPolyDataSMPlugin PROPERTY FOLDER "MantidVatesParaViewPlugins")

target_link_libraries( MantidParaViewThresholdPolyDataSMPlugin LINK_PRIVATE ${TCMALLOC_LIBRARIES_LINKTIME} 
${MANTID_SUBPROJECT_LIBS} 
${vtkjsoncpp_LIBRARIES}
)

if (OSX_VERSION VERSION_GREATER 10.8)
  set_target_properties ( MantidParaViewThresholdPolyDataSMPlugin PROPERTIES INSTALL_RPATH "@loader_path/../../Contents/Libraries;@loader_path/../../Contents/MacOS")
endif ()

# Put library into subfolder.
SET_TARGET_OUTPUT_DIRECTORY(MantidParaViewThresholdPolyDataSMPlugin  ${CMAKE_LIBRARY_OUTPUT_DIRECTORY}/${CMAKE_CFG_INTDIR}/${PVPLUGINS_DIR}/${PVPLUGINS_SUBDIR})

install( TARGETS MantidParaViewThresholdPolyDataSMPlugin ${SYSTEM_PACKAGE_TARGET} DESTINATION ${PVPLUGINS_DIR}/${PVPLUGINS_SUBDIR})

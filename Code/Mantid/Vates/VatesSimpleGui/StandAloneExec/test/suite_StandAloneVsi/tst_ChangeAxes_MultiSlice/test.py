
def main():
    source(findFile("scripts", "test_helpers.py"))
    source(findFile("scripts", "common_checks.py"))
    startApplication("VatesSimpleGui")
    open_file("MDEW_4D.nxs")

    clickButton(waitForObject(":splitter_2.Rebin_QPushButton"))
    set_ptw_lineedit_property(100, "Bins")
    set_ptw_lineedit_property(100, "Bins", "2")
    set_ptw_lineedit_property(100, "Bins", "3")
    set_ptw_lineedit_property(3, "Bins", "4")
    apply_ptw_settings()

    switch_mode("multiSlice")
    
    # Num slices: X = 3, Y = 2, Z = 1
    make_slice("xAxisWidget", 0.0)
    make_slice("yAxisWidget", 0.0)
    make_slice("zAxisWidget", 0.0)
    make_slice("xAxisWidget", 1.0)
    make_slice("yAxisWidget", 1.0)
    make_slice("xAxisWidget", -1.0)
    apply_ptw_settings()
  
    mouseClick(waitForObject(":splitter.pipelineBrowser_pqPipelineBrowserWidget"), 51, 56, 0, Qt.LeftButton)
    
    # Change the axis orientations
    set_ptw_combobox_property("E", 1)
    apply_ptw_settings()

    check_axis_parameters("xAxisWidget", "E", 0.0, 3.0)
    
    check_slices("xAxisWidget", 0)
    check_slices("yAxisWidget", 2)
    check_slices("zAxisWidget", 1)
        
def set_ptw_combobox_property(property, index):
    object = ":ScrollArea.%s_QComboBox" % property
    combobox = waitForObject(object)
    comboboxItem = combobox.itemText(index)
    clickItem(object, comboboxItem, 5, 5, 0, Qt.LeftButton)
    
def check_axis_parameters(axisScaleName, title, min, max):
    axisScale = waitForObject(":splitter_2.%s_Mantid::Vates::SimpleGui::AxisInteractor" % axisScaleName)
    min_curr = axisScale.getMinimum
    max_curr = axisScale.getMaximum
    title_curr = axisScale.getTitle
    
    test.compare(title, title_curr)
    test.compare(min, min_curr)
    test.compare(max, max_curr)

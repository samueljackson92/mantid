#pylint: disable=invalid-name
"""
    Script used to start the Test Interface from MantidPlot
"""
from ui.developer_workshop_reference import developer_workshop_reference_gui

ui = developer_workshop_reference_gui.DeveloperWorkshopReferenceGui()
if ui.setup_layout():
    ui.show()

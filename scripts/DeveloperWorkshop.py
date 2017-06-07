#pylint: disable=invalid-name
"""
    Script used to start the Test Interface from MantidPlot
"""
from ui.developer_workshop import developer_workshop_gui

ui = developer_workshop_gui.DeveloperWorkshopGui()
if ui.setup_layout():
    ui.show()

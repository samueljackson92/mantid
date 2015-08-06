#pylint: disable=no-init
from mantid.api import PythonAlgorithm, AlgorithmFactory, MatrixWorkspaceProperty, PropertyMode, \
    ITableWorkspaceProperty, FileAction, FileProperty
from mantid.kernel import Direction, FloatBoundedValidator, PropertyCriterion, EnabledWhenProperty, logger
import mantid.simpleapi as api
from scipy.stats import chisquare
from scipy.optimize import minimize
import numpy as np

class AlignComponents(PythonAlgorithm):
    """ Class to align components
    """

    def category(self):
        """ Mantid required
        """
        return "PythonAlgorithms;Diffraction"

    def name(self):
        """ Mantid required
        """
        return "AlignComponents"

    def summary(self):
        """ Mantid required
        """
        return "Align a component by minimising difference to an offset workspace"

    def PyInit(self):
        self.declareProperty(ITableWorkspaceProperty("CalibrationTable",
                                                     "",
                                                     optional=PropertyMode.Mandatory,
                                                     direction=Direction.Input),
                             doc="Calibration table, currently only uses difc")
        self.declareProperty(MatrixWorkspaceProperty("MaskWorkspace",
                                                     "",
                                                     optional=PropertyMode.Optional,
                                                     direction=Direction.Input),
                             doc="Mask workspace")
        self.declareProperty(FileProperty(name="InstrumentFilename",
                                          defaultValue="",
                                          action=FileAction.Load,
                                          extensions=[".xml"]),
                             doc="Instrument filename")
        self.declareProperty("ComponentList", "",
                             direction=Direction.Input,
                             doc="Comma separated list on instrument components to refine.")
        # X position
        self.declareProperty(name="PosX", defaultValue=True,
                             doc="Refine X position")
        condition = EnabledWhenProperty("PosX", PropertyCriterion.IsDefault)
        self.declareProperty(name="MinX", defaultValue=-0.1,
                             validator=FloatBoundedValidator(-10.0, 10.0),
                             doc="Minimum relative X bound (m)")
        self.setPropertySettings("MinX", condition)
        self.declareProperty(name="MaxX", defaultValue=0.1,
                             validator=FloatBoundedValidator(),
                             doc="Maximum relative X bound (m)")
        self.setPropertySettings("MaxX", condition)
        # Y position
        self.declareProperty(name="PosY", defaultValue=True,
                             doc="Refine Y position")
        condition = EnabledWhenProperty("PosY", PropertyCriterion.IsDefault)
        self.declareProperty(name="MinY", defaultValue=-0.1,
                             validator=FloatBoundedValidator(-10.0, 10.0),
                             doc="Minimum relative Y bound (m)")
        self.setPropertySettings("MinY", condition)
        self.declareProperty(name="MaxY", defaultValue=0.1,
                             validator=FloatBoundedValidator(),
                             doc="Maximum relative Y bound (m)")
        self.setPropertySettings("MaxY", condition)
        # Z position
        self.declareProperty(name="PosZ", defaultValue=True,
                             doc="Refine Z position")
        condition = EnabledWhenProperty("PosZ", PropertyCriterion.IsDefault)
        self.declareProperty(name="MinZ", defaultValue=-0.1,
                             validator=FloatBoundedValidator(-10.0, 10.0),
                             doc="Minimum relative Z bound (m)")
        self.setPropertySettings("MinZ", condition)
        self.declareProperty(name="MaxZ", defaultValue=0.1,
                             validator=FloatBoundedValidator(),
                             doc="Maximum relative Z bound(m)")
        self.setPropertySettings("MaxZ", condition)
        """
        # X rotation
        self.declareProperty(name="RotX", defaultValue=True,
                             doc="Refine rotation around X")
        condition=VisibleWhenProperty("RotX",PropertyCriterion.IsDefault)
        self.declareProperty(name="MinRotX", defaultValue=-10.0,
                             validator=FloatBoundedValidator(),
                             doc="Minimum relative X rotation")
        self.setPropertySettings("MinRotX", condition)
        self.declareProperty(name="MaxRotX", defaultValue=10.0,
                             validator=FloatBoundedValidator(),
                             doc="Maximum relative X rotation")
        self.setPropertySettings("MaxRotX", condition)
        # Y rotation
        self.declareProperty(name="RotY", defaultValue=True,
                             doc="Refine rotation around Y")
        condition=VisibleWhenProperty("RotY",PropertyCriterion.IsDefault)
        self.declareProperty(name="MinRotY", defaultValue=-10.0,
                             validator=FloatBoundedValidator(),
                             doc="Minimum relative Y rotation")
        self.setPropertySettings("MinRotY", condition)
        self.declareProperty(name="MaxRotY", defaultValue=10.0,
                             validator=FloatBoundedValidator(),
                             doc="Maximum relative Y rotation")
        self.setPropertySettings("MaxRotY", condition)
        # Z rotation
        self.declareProperty(name="RotZ", defaultValue=True,
                             doc="Refine rotation around Z")
        condition=VisibleWhenProperty("RotZ",PropertyCriterion.IsDefault)
        self.declareProperty(name="MinRotZ", defaultValue=-10.0,
                             validator=FloatBoundedValidator(),
                             doc="Minimum relative Z rotation")
        self.setPropertySettings("MinRotZ", condition)
        self.declareProperty(name="MaxRotZ", defaultValue=10.0,
                             validator=FloatBoundedValidator(),
                             doc="Maximum relative Z rotation")
        self.setPropertySettings("MaxRotZ", condition)
        """

    def validateInputs(self):
        """
        Does basic validation for inputs
        """
        issues = dict()
        calWS = self.getProperty('CalibrationTable').value
        if 'difc' not in calWS.getColumnNames() or 'detid' not in calWS.getColumnNames():
            issues['CalibrationTable'] = "Calibration table requires detid and difc"
        # maskWS = self.getProperty("MaskWorkspace").value
        # if maskWS != '':
        #    issues['MaskWorkspace'] = "MaskWorkspace must be of type \"MaskWorkspace\""
        instrumentWS = api.LoadEmptyInstrument(Filename=self.getProperty("InstrumentFilename").value)
        components = self.getProperty("ComponentList").value.split(',')
        for component in components:
            if instrumentWS.getInstrument().getComponentByName(component) is None:
                issues['ComponentList'] = "Instrument has no component \"" + component + "\""
        if not (self.getProperty("PosX").value + self.getProperty("PosY").value + self.getProperty("PosZ").value):
            issues["PosX"] = "You must refine something"
        return issues

    def PyExec(self):
        calWS = self.getProperty('CalibrationTable').value
        difc = calWS.column('difc')
        instrumentWS = api.LoadEmptyInstrument(Filename=self.getProperty("InstrumentFilename").value)
        components = self.getProperty("ComponentList").value.split(',')
        optionsList = ["PosX", "PosY", "PosZ"]
        optionsDict = {}
        for opt in optionsList:
            optionsDict[opt] = self.getProperty(opt).value
        for component in components:
            comp = instrumentWS.getInstrument().getComponentByName(component)
            logger.notice("Working on " + comp.getFullName())
            firstDetID = self._getFirstDetID(comp)
            lastDetID = self._getLastDetID(comp)
            logger.debug(" Initial position is " + str(comp.getPos()) +
                         " Initial rotation is " + str(comp.getRotation().getEulerAngles()) +
                         " First DetID = " + str(firstDetID) +
                         " Last DetID = " + str(lastDetID))
            # TODO: get mask, mask difc
            x0List = []
            initialPos = [comp.getPos().getX(), comp.getPos().getY(), comp.getPos().getZ()]
            boundsList = []
            if optionsDict["PosX"]:
                x0List.append(initialPos[0])
                boundsList.append((initialPos[0] + self.getProperty("MinX").value,
                               initialPos[0] + self.getProperty("MaxX").value))
            if optionsDict["PosY"]:
                x0List.append(initialPos[1])
                boundsList.append((initialPos[1] + self.getProperty("MinY").value,
                               initialPos[1] + self.getProperty("MaxY").value))
            if optionsDict["PosZ"]:
                x0List.append(initialPos[2])
                boundsList.append((initialPos[2] + self.getProperty("MinZ").value,
                               initialPos[2] + self.getProperty("MaxZ").value))
            results = minimize(self._minimisation_func, x0=x0List,
                               args=(instrumentWS,
                                     comp.getFullName(),
                                     firstDetID,
                                     lastDetID,
                                     difc[firstDetID:lastDetID+1],
                                     optionsDict,
                                     initialPos),
                               bounds=boundsList)
            print results

    def _minimisation_func(self, x0, ws, component, firstDetID, lastDetID, difc, optionsDict, initialPos):
        optionsList = ["PosX", "PosY", "PosZ"]
        x0_index = 0
        x = []
        for opt in optionsList:
            if optionsDict[opt]:
                x.append(x0[x0_index])
                x0_index += 1
            else:
                x.append(initialPos[optionsList.index(opt)])
        api.MoveInstrumentComponent(ws, component, X=x[0], Y=x[1], Z=x[2], RelativePosition=False)
        new_difc = api.CalculateDIFC(ws)
        difc_new = new_difc.extractY().flatten()[firstDetID:lastDetID+1]
        logger.debug("chisquare = " + str(chisquare(f_obs=difc, f_exp=difc_new)[0]))
        return chisquare(f_obs=difc, f_exp=difc_new)[0]

    def _getFirstDetID(self, component):
        """
        recursive search to find first detID
        """
        if component.type() == 'DetectorComponent':
            return component.getID()
        else:
            return self._getFirstDetID(component[0])

    def _getLastDetID(self, component):
        """
        recursive search to find last detID
        """
        if component.type() == 'DetectorComponent':
            return component.getID()
        else:
            return self._getLastDetID(component[component.nelements() - 1])


AlgorithmFactory.subscribe(AlignComponents)

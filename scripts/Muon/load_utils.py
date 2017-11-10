from __future__ import (absolute_import, division, print_function)
import mantid.simpleapi as mantid


class LoadUtils(object):
    """
    A simple class for identifing the current run
    and it can return the name, run and instrument.
    The current run is the same as the one in MonAnalysis
    """
    def __init__(self, parent=None):
        if self.MuonAnalysisExists():
            # get everything from the ADS
            self.options = mantid.AnalysisDataService.getObjectNames()
            self.options = [item.replace(" ","") for item in self.options]
            tmpWS=mantid.AnalysisDataService.retrieve("MuonAnalysis")
            self.instrument=tmpWS.getInstrument().getName()
            self.runName=self.instrument+str(tmpWS.getRunNumber()).zfill(8)

        else:
            mantid.logger.error("Muon Analysis workspace does not exist - no data loaded")

    # get methods
    def getCurrentWS(self):
        return self.runName, self.options

    def getRunName(self):
        return self.runName

    def getInstrument(self):
        return self.instrument

    # check if muon analysis exists
    def MuonAnalysisExists(self):
        # if period data look for the first period
        if mantid.AnalysisDataService.doesExist("MuonAnalysis_1"):
            return True
        else:
            # if its not period data
            return mantid.AnalysisDataService.doesExist("MuonAnalysis")

    # Get the groups/pairs for active WS
    # ignore raw files
    def getWorkspaceNames(self):
        # gets all WS in the ADS
        runName,options = self.getCurrentWS()
        final_options=[]
        # only keep the relevant WS (same run as Muon Analysis)
        for pick in options:
            if ";" in pick and "Raw" not in pick and runName in pick:
                final_options.append(pick)
        return final_options

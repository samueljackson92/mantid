// Mantid Repository : https://github.com/mantidproject/mantid
//
// Copyright &copy; 2018 ISIS Rutherford Appleton Laboratory UKRI,
//     NScD Oak Ridge National Laboratory, European Spallation Source
//     & Institut Laue - Langevin
// SPDX - License - Identifier: GPL - 3.0 +
/*
 * SCDCalibratePanelsTest.h
 *
 *  Created on: Mar 12, 2012
 *      Author: ruth
 */

#ifndef SCDCALIBRATEPANELSTEST_H_
#define SCDCALIBRATEPANELSTEST_H_

#include "MantidAPI/AnalysisDataService.h"
#include "MantidCrystal/SCDCalibratePanels.h"
#include <cxxtest/TestSuite.h>

using namespace Mantid::API;
using namespace Mantid::DataObjects;
using namespace std;
using namespace Mantid::Geometry;
using namespace Mantid::Kernel;
using namespace Mantid::Crystal;

class SCDCalibratePanelsTest : public CxxTest::TestSuite {

public:
    /*
  void est_TOPAZ_5637() {
    // load a peaks file
    boost::shared_ptr<Algorithm> alg =
        AlgorithmFactory::Instance().create("LoadIsawPeaks", 1);
    alg->initialize();
    alg->setPropertyValue("Filename", "Peaks5637.integrate");
    alg->setPropertyValue("OutputWorkspace", "TOPAZ_5637");
    TS_ASSERT(alg->execute());

    // run the calibration
    alg = AlgorithmFactory::Instance().create("SCDCalibratePanels", 1);
    alg->initialize();
    // Peakws->setName("PeaksWsp");
    alg->setPropertyValue("PeakWorkspace", "TOPAZ_5637");
    alg->setProperty("a", 4.75);
    alg->setProperty("b", 4.75);
    alg->setProperty("c", 13.0);
    alg->setProperty("alpha", 90.0);
    alg->setProperty("beta", 90.0);
    alg->setProperty("gamma", 120.0);
    alg->setPropertyValue("DetCalFilename", "/tmp/topaz.detcal"); // deleteme
    TS_ASSERT(alg->execute());

    // verify the results
    ITableWorkspace_sptr results =
        AnalysisDataService::Instance().retrieveWS<ITableWorkspace>(
            "params_bank47");
    // TODO: Some of the fit parameters that are below are extermly sensitive to
    // rounding errors in the algorithm LoadIsawPeaks and floating point math in
    // the instrument code. Ideally the assertions should be on something else.
    TS_ASSERT_DELTA(-0.0050, results->cell<double>(0, 1), 1e-3);
    TS_ASSERT_DELTA(0.0013, results->cell<double>(1, 1), 4e-4);
    TS_ASSERT_DELTA(0.0008, results->cell<double>(2, 1), 3e-4);
    TS_ASSERT_DELTA(0.0, results->cell<double>(3, 1), 1.2);
    TS_ASSERT_DELTA(0.0, results->cell<double>(4, 1), 1.1);
    TS_ASSERT_DELTA(0.1133, results->cell<double>(5, 1), 0.36);
    TS_ASSERT_DELTA(1.0024, results->cell<double>(6, 1), 5e-3);
    TS_ASSERT_DELTA(0.9986, results->cell<double>(7, 1), 1e-2);
    TS_ASSERT_DELTA(0.2710, results->cell<double>(9, 1), 0.2);
    ITableWorkspace_sptr resultsL1 =
        AnalysisDataService::Instance().retrieveWS<ITableWorkspace>(
            "params_L1");
    TS_ASSERT_DELTA(-0.00761, resultsL1->cell<double>(2, 1), .01);
  }*/


  void test_WISH_with_ruby_strong_peaks() {
    const auto workspace_name = "WISH_41611_strong_peaks";
    const auto loader = AlgorithmFactory::Instance().create("LoadNexus", 1);

    loader->initialize();
    loader->setPropertyValue("Filename", "WISH_41611_strong_peaks.nxs");
    loader->setPropertyValue("OutputWorkspace", workspace_name);
    TS_ASSERT(loader->execute());

    // run the calibration
    auto alg = AlgorithmFactory::Instance().create("SCDCalibratePanels", 1);
    alg->initialize();
    // Peakws->setName("PeaksWsp");
    alg->setPropertyValue("PeakWorkspace", workspace_name);
    alg->setProperty("a", 4.75);
    alg->setProperty("b", 4.75);
    alg->setProperty("c", 13.0);
    alg->setProperty("alpha", 90.0);
    alg->setProperty("beta", 90.0);
    alg->setProperty("gamma", 120.0);
    alg->setPropertyValue("DetCalFilename", "/tmp/wish.detcal"); // deleteme
    TS_ASSERT(alg->execute());

    // verify the results
    ITableWorkspace_sptr results =
        AnalysisDataService::Instance().retrieveWS<ITableWorkspace>(
            "params_bank01");
    // TODO: Some of the fit parameters that are below are extermly sensitive to
    // rounding errors in the algorithm LoadIsawPeaks and floating point math in
    // the instrument code. Ideally the assertions should be on something else.
    TS_ASSERT_DELTA(-0.0050, results->cell<double>(0, 1), 1e-3);
    TS_ASSERT_DELTA(0.0013, results->cell<double>(1, 1), 4e-4);
    TS_ASSERT_DELTA(0.0008, results->cell<double>(2, 1), 3e-4);
    TS_ASSERT_DELTA(0.0, results->cell<double>(3, 1), 1.2);
    TS_ASSERT_DELTA(0.0, results->cell<double>(4, 1), 1.1);
    TS_ASSERT_DELTA(0.1133, results->cell<double>(5, 1), 0.36);
    TS_ASSERT_DELTA(1.0024, results->cell<double>(6, 1), 5e-3);
    TS_ASSERT_DELTA(0.9986, results->cell<double>(7, 1), 1e-2);
    TS_ASSERT_DELTA(0.2710, results->cell<double>(9, 1), 0.2);
    ITableWorkspace_sptr resultsL1 =
        AnalysisDataService::Instance().retrieveWS<ITableWorkspace>(
            "params_L1");
    TS_ASSERT_DELTA(-0.00761, resultsL1->cell<double>(2, 1), .01);
  }
};

#endif /* SCDCALIBRATEPANELSTEST_H_ */

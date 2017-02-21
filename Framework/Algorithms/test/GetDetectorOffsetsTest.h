#ifndef GETDETECTOROFFSETSTEST_H_
#define GETDETECTOROFFSETSTEST_H_

#include "MantidAlgorithms/GetDetectorOffsets.h"

#include "MantidAPI/AlgorithmManager.h"
#include "MantidAPI/AnalysisDataService.h"
#include "MantidAPI/Axis.h"
#include "MantidAPI/DetectorInfo.h"
#include "MantidAPI/FileFinder.h"
#include "MantidAPI/FrameworkManager.h"
#include "MantidDataObjects/OffsetsWorkspace.h"
#include "MantidKernel/UnitFactory.h"
#include "MantidTestHelpers/FileComparisonHelper.h"
#include "MantidTestHelpers/WorkspaceCreationHelper.h"

#include <Poco/File.h>
#include <Poco/Path.h>

#include <cxxtest/TestSuite.h>
#include <iostream>

using namespace Mantid::API;
using Mantid::Algorithms::GetDetectorOffsets;
using Mantid::DataObjects::OffsetsWorkspace_sptr;

class GetDetectorOffsetsTest : public CxxTest::TestSuite {
public:
  // This pair of boilerplate methods prevent the suite being created statically
  // This means the constructor isn't called when running other tests
  static GetDetectorOffsetsTest *createSuite() {
    return new GetDetectorOffsetsTest();
  }
  static void destroySuite(GetDetectorOffsetsTest *suite) { delete suite; }

  GetDetectorOffsetsTest() {
    // We require the Framework manager to be started for these tests
    Mantid::API::FrameworkManager::Instance();
  }

  void testTheBasics() {
    GetDetectorOffsets offsets;
    TS_ASSERT_EQUALS(offsets.name(), "GetDetectorOffsets");
    TS_ASSERT_EQUALS(offsets.version(), 1);
  }

  void testInit() {
    GetDetectorOffsets offsets;
    TS_ASSERT_THROWS_NOTHING(offsets.initialize());
    TS_ASSERT(offsets.isInitialized());
  }

  void testExec() {
    // ---- Create the simple workspace -------
    MatrixWorkspace_sptr WS =
        WorkspaceCreationHelper::create2DWorkspaceWithFullInstrument(1, 200);
    WS->getAxis(0)->unit() =
        Mantid::Kernel::UnitFactory::Instance().create("dSpacing");

    populateWsWithData(WS.get());

    const std::string outputWS("offsetsped");
    const std::string maskWS("masksped");

    GetDetectorOffsets alg;
    setupCommonAlgProperties(alg, WS, outputWS, maskWS);

    TS_ASSERT_THROWS_NOTHING(alg.execute());
    TS_ASSERT(alg.isExecuted());

    MatrixWorkspace_const_sptr output;
    TS_ASSERT_THROWS_NOTHING(
        output = AnalysisDataService::Instance().retrieveWS<MatrixWorkspace>(
            outputWS));
    if (!output)
      return;

    TS_ASSERT_DELTA(output->y(0)[0], -0.0196, 0.0001);

    AnalysisDataService::Instance().remove(outputWS);

    MatrixWorkspace_const_sptr mask;
    TS_ASSERT_THROWS_NOTHING(
        mask = AnalysisDataService::Instance().retrieveWS<MatrixWorkspace>(
            maskWS));
    if (!mask)
      return;
    TS_ASSERT(!mask->detectorInfo().isMasked(0));
  }

  void testExecWithGroup() {
    // --------- Workspace with summed spectra -------
    MatrixWorkspace_sptr WS =
        WorkspaceCreationHelper::createGroupedWorkspace2D(3, 200, 1.0);
    WS->getAxis(0)->unit() =
        Mantid::Kernel::UnitFactory::Instance().create("dSpacing");

    populateWsWithData(WS.get());

    GetDetectorOffsets alg;
    const std::string outputWS("offsetsped");
    const std::string maskWS("masksped");
    setupCommonAlgProperties(alg, WS, outputWS, maskWS);

    TS_ASSERT_THROWS_NOTHING(alg.execute());
    TS_ASSERT(alg.isExecuted());

    OffsetsWorkspace_sptr output = alg.getProperty("OutputWorkspace");
    if (!output)
      return;

    TS_ASSERT_DELTA(output->getValue(1), -0.0196, 0.0001);
    TS_ASSERT_EQUALS(output->getValue(1), output->getValue(2));
    TS_ASSERT_EQUALS(output->getValue(1), output->getValue(3));

    AnalysisDataService::Instance().remove(outputWS);

    MatrixWorkspace_const_sptr mask;
    TS_ASSERT_THROWS_NOTHING(
        mask = AnalysisDataService::Instance().retrieveWS<MatrixWorkspace>(
            maskWS));
    if (!mask)
      return;
    TS_ASSERT(!mask->detectorInfo().isMasked(0));
  }

  void testExecAbsolute() {
    // ---- Create the simple workspace -------
    MatrixWorkspace_sptr WS =
        WorkspaceCreationHelper::create2DWorkspaceWithFullInstrument(1, 200);
    WS->getAxis(0)->unit() =
        Mantid::Kernel::UnitFactory::Instance().create("dSpacing");

    populateWsWithData(WS.get());

    const std::string outputWS("offsetsped");
    const std::string maskWS("masksped");

    GetDetectorOffsets alg;
    setupCommonAlgProperties(alg, WS, outputWS, maskWS);

    TS_ASSERT_THROWS_NOTHING(alg.setPropertyValue("MaxOffset", "10"));
    TS_ASSERT_THROWS_NOTHING(alg.setPropertyValue("OffsetMode", "Absolute"));
    TS_ASSERT_THROWS_NOTHING(alg.setPropertyValue("DIdeal", "3.5"));
    TS_ASSERT_THROWS_NOTHING(alg.execute());
    TS_ASSERT(alg.isExecuted());

    MatrixWorkspace_const_sptr output;
    TS_ASSERT_THROWS_NOTHING(
        output = AnalysisDataService::Instance().retrieveWS<MatrixWorkspace>(
            outputWS));
    if (!output)
      return;

    TS_ASSERT_DELTA(output->y(0)[0], 2.4803, 0.0001);

    AnalysisDataService::Instance().remove(outputWS);

    MatrixWorkspace_const_sptr mask;
    TS_ASSERT_THROWS_NOTHING(
        mask = AnalysisDataService::Instance().retrieveWS<MatrixWorkspace>(
            maskWS));
    if (!mask)
      return;
    TS_ASSERT(!mask->detectorInfo().isMasked(0));
  }

  void test_groupingFile() {
    // Setup various paths we will be using
    const std::string referenceFileName("GetDetectorsOffsetReference.cal");
    const std::string outFileName("GetDetectorsOffsetTest.cal");

    auto fileHandle = getOutFileHandle(outFileName);
    const std::string fullRefPath =
        FileFinder::Instance().getFullPath(referenceFileName);

    TSM_ASSERT_DIFFERS("Reference file not found", fullRefPath, "");

    // Create workspace with 10 detectors and 200 bins each
    MatrixWorkspace_sptr ws =
        WorkspaceCreationHelper::create2DWorkspaceWithFullInstrument(
            10, 200, false, false, true, "POLARIS");
    ws->getAxis(0)->unit() =
        Mantid::Kernel::UnitFactory::Instance().create("dSpacing");

    populateWsWithData(ws.get());

    const std::string outputWS("offsetsped");
    const std::string maskWS("masksped");

    GetDetectorOffsets alg;
    setupCommonAlgProperties(alg, ws, outputWS, maskWS);
    alg.setProperty("GroupingFileName", fileHandle.path());
    TS_ASSERT_THROWS_NOTHING(alg.execute());
    TS_ASSERT(calFileEqualityCheck(fullRefPath, fileHandle.path()));
    fileHandle.remove();
  }

private:
  Poco::File getOutFileHandle(const std::string &outName) {
    Poco::Path tempPath(Poco::Path::temp());
    tempPath.append(outName);
    Poco::File tempFile(tempPath.toString());
    return tempFile;
  }

  bool calFileEqualityCheck(const std::string &refFilePath,
                            const std::string &outFile) {
    // Have to skip first line as it contains a date-time stamp
    std::ifstream refStream(refFilePath);
    std::ifstream outStream(outFile);

    auto skipLine = [](std::ifstream &s) {
      s.ignore(std::numeric_limits<std::streamsize>::max(), '\n');
    };

    skipLine(refStream);
    skipLine(outStream);

    return FileComparisonHelper::compareFileStreams(refStream, outStream);
  }

  void GetDetectorOffsetsTest::populateWsWithData(MatrixWorkspace *ws) {
    auto xvals = ws->points(0);
    // loop through xvals, calculate and set to Y
    std::transform(
        xvals.cbegin(), xvals.cend(), ws->mutableY(0).begin(),
        [](const double x) { return exp(-0.5 * pow((x - 1) / 10.0, 2)); });

    auto &E = ws->mutableE(0);
    E.assign(E.size(), 0.001);
  }

  void GetDetectorOffsetsTest::setupCommonAlgProperties(
      GetDetectorOffsets &alg, const MatrixWorkspace_sptr &inputWS,
      const std::string &outputWSName, const std::string maskedWSName) {
    alg.initialize();
    TS_ASSERT_THROWS_NOTHING(alg.setProperty("InputWorkspace", inputWS));
    TS_ASSERT_THROWS_NOTHING(
        alg.setPropertyValue("OutputWorkspace", outputWSName));
    TS_ASSERT_THROWS_NOTHING(
        alg.setPropertyValue("MaskWorkspace", maskedWSName));
    TS_ASSERT_THROWS_NOTHING(alg.setPropertyValue("Step", "0.02"));
    TS_ASSERT_THROWS_NOTHING(alg.setPropertyValue("DReference", "1.00"));
    TS_ASSERT_THROWS_NOTHING(alg.setPropertyValue("XMin", "-20"));
    TS_ASSERT_THROWS_NOTHING(alg.setPropertyValue("XMax", "20"));
    alg.setRethrows(true);
  }
};

class GetDetectorOffsetsTestPerformance : public CxxTest::TestSuite {
  MatrixWorkspace_sptr WS;
  int numpixels;

public:
  static GetDetectorOffsetsTestPerformance *createSuite() {
    return new GetDetectorOffsetsTestPerformance();
  }
  static void destroySuite(GetDetectorOffsetsTestPerformance *suite) {
    delete suite;
  }

  GetDetectorOffsetsTestPerformance() { FrameworkManager::Instance(); }

  void setUp() override {
    numpixels = 10000;
    WS = WorkspaceCreationHelper::create2DWorkspaceWithFullInstrument(
        numpixels, 200, false);
    WS->getAxis(0)->unit() =
        Mantid::Kernel::UnitFactory::Instance().create("dSpacing");
    for (size_t wi = 0; wi < WS->getNumberHistograms(); wi++) {

      auto xvals = WS->points(wi);
      auto &Y = WS->mutableY(wi);

      std::transform(
          xvals.cbegin(), xvals.cend(), Y.begin(),
          [](const double x) { return exp(-0.5 * pow((x - 1) / 10.0, 2)); });
      auto &E = WS->mutableE(wi);
      E.assign(E.size(), 0.001);
    }
  }

  void test_performance() {
    AlgorithmManager::Instance(); // Initialize here to avoid an odd ABORT
    GetDetectorOffsets offsets;
    if (!offsets.isInitialized())
      offsets.initialize();
    TS_ASSERT_THROWS_NOTHING(offsets.setProperty("InputWorkspace", WS));
    TS_ASSERT_THROWS_NOTHING(offsets.setPropertyValue("Step", "0.02"));
    TS_ASSERT_THROWS_NOTHING(offsets.setPropertyValue("DReference", "1.00"));
    TS_ASSERT_THROWS_NOTHING(offsets.setPropertyValue("XMin", "-20"));
    TS_ASSERT_THROWS_NOTHING(offsets.setPropertyValue("XMax", "20"));
    TS_ASSERT_THROWS_NOTHING(
        offsets.setPropertyValue("OutputWorkspace", "dummyname"));
    TS_ASSERT_THROWS_NOTHING(offsets.execute());
    TS_ASSERT(offsets.isExecuted());
    OffsetsWorkspace_sptr output;
    TS_ASSERT_THROWS_NOTHING(output = offsets.getProperty("OutputWorkspace"));
    if (!output)
      return;
    TS_ASSERT_DELTA(output->mutableY(0)[0], -0.0196, 0.0001);
  }
};

#endif /*GETDETECTOROFFSETSTEST_H_*/

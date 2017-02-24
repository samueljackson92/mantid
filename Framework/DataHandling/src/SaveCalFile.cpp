#include "MantidAPI/DetectorInfo.h"
#include "MantidAPI/FileProperty.h"
#include "MantidAPI/SpectrumInfo.h"
#include "MantidDataHandling/SaveCalFile.h"
#include "MantidKernel/System.h"
#include "MantidKernel/BoundedValidator.h"
#include "MantidTypes/SpectrumDefinition.h"

#include <algorithm>
#include <cmath>
#include <fstream>
#include <utility>
#include <vector>

using namespace Mantid::Kernel;
using namespace Mantid::API;
using namespace Mantid::DataObjects;
using namespace Mantid::Geometry;

namespace Mantid {
namespace DataHandling {

// Register the algorithm into the AlgorithmFactory
DECLARE_ALGORITHM(SaveCalFile)

//----------------------------------------------------------------------------------------------
/** Initialize the algorithm's properties.
 */
void SaveCalFile::init() {
  declareProperty(
      make_unique<WorkspaceProperty<GroupingWorkspace>>(
          "GroupingWorkspace", "", Direction::Input, PropertyMode::Optional),
      "Optional: An GroupingWorkspace workspace giving the grouping info.");

  declareProperty(
      make_unique<WorkspaceProperty<OffsetsWorkspace>>(
          "OffsetsWorkspace", "", Direction::Input, PropertyMode::Optional),
      "Optional: An OffsetsWorkspace workspace giving the detector calibration "
      "values.");

  declareProperty(
      make_unique<WorkspaceProperty<MaskWorkspace>>(
          "MaskWorkspace", "", Direction::Input, PropertyMode::Optional),
      "Optional: An Workspace workspace giving which detectors are masked.");

  declareProperty(
      make_unique<FileProperty>("Filename", "", FileProperty::Save, ".cal"),
      "Path to the .cal file that will be created.");

  declareProperty<bool>("Sort Detector IDs", true,
                        "If true this sorts the output calibration file by "
                        "detector ID (default). If set to false it preserves "
                        "the detector ID order found in the workspace",
                        Direction::Input);

  auto offsetprecision = boost::make_shared<BoundedValidator<int>>();
  offsetprecision->setLower(7);
  offsetprecision->setUpper(11);
  declareProperty("OffsetPrecision", 7, offsetprecision,
                  "Precision of offsets (between 7 and 11 decimal).");
}

//----------------------------------------------------------------------------------------------
/** Execute the algorithm.
 */
void SaveCalFile::exec() {
  GroupingWorkspace_sptr groupWS = getProperty("GroupingWorkspace");
  OffsetsWorkspace_sptr offsetsWS = getProperty("OffsetsWorkspace");
  MaskWorkspace_sptr maskWS = getProperty("MaskWorkspace");
  std::string Filename = getPropertyValue("Filename");
  m_precision = getProperty("OffsetPrecision");

  // Do the saving
  SaveCalFile::saveCalFile(Filename, groupWS, offsetsWS, maskWS);
}

/**
  * Gets the detector IDs and associated spectrum index for them
  * and stores them in a vector of pairs
  *
  * @param ws :: The workspace to pull detector IDs from
  *
  * @return :: A vector containing pairs of detector IDs and their spectrum
  *index position
  */
template <typename T>
std::vector<std::pair<Mantid::detid_t, size_t>>
SaveCalFile::createDetectorToSpectrumMapping(const T *ws) {
  const size_t numHisto = ws->getNumberHistograms();

  // Create mappings for detector Positions to ID and detector ID to spectrum
  // Maps
  std::vector<std::pair<Mantid::detid_t, size_t>> detIDToSpectrumMap;
  std::vector<std::pair<size_t, Mantid::detid_t>> detPositionToIDMap;
  detIDToSpectrumMap.reserve(numHisto);
  detPositionToIDMap.reserve(numHisto);

  const API::DetectorInfo &detectorInfo = ws->detectorInfo();
  const API::SpectrumInfo &spectrumInfo = ws->spectrumInfo();
  const auto &detectorIDs = detectorInfo.detectorIDs();

  // Create a lambda for comparing elements later
  auto comparator =
      [](const auto &a, const auto &b) { return a.first < b.first; };

  // Don't take reference as detid_t is primitive type
  // Get a mapping of detector positions to detector IDs we will use later
  for (const auto detID : detectorIDs) {
    detPositionToIDMap.push_back(
        std::make_pair(detectorInfo.indexOf(detID), detID));
  }
  // Sort so we don't have to parse the entire container
  std::sort(detPositionToIDMap.begin(), detPositionToIDMap.end(), comparator);

  for (size_t specIndex = 0; specIndex < numHisto; specIndex++) {
    const auto &specDef = spectrumInfo.spectrumDefinition(specIndex);
    // Spectrum definition holds the detector index as the first element
    for (size_t i = 0; i < specDef.size(); i++) {
      const auto &spectrumPair = specDef[i];
      // As container is sorted use lower bound to implement search
      const auto it =
          std::lower_bound(detPositionToIDMap.cbegin(),
                           detPositionToIDMap.cend(), spectrumPair, comparator);

      if (it != detPositionToIDMap.end()) {
        // If we found it we take the detector ID and map it to the spectrum
        // index
        detIDToSpectrumMap.push_back(std::make_pair((*it).second, specIndex));
      } else {
        continue;
      }
    }
  }
  return detIDToSpectrumMap;
}
//-----------------------------------------------------------------------
/** Reads the calibration file.
 *
 * @param calFileName :: path to the old .cal file
 * @param groupWS :: optional, GroupingWorkspace to save. Will be 0 if not
 *specified.
 * @param offsetsWS :: optional, OffsetsWorkspace to save. Will be 0.0 if not
 *specified.
 * @param maskWS :: optional, masking-type workspace to save. Will be 1
 *(selected) if not specified.
 */
void SaveCalFile::saveCalFile(const std::string &calFileName,
                              GroupingWorkspace_sptr groupWS,
                              OffsetsWorkspace_sptr offsetsWS,
                              MaskWorkspace_sptr maskWS) {

  Instrument_const_sptr inst;

  std::vector<detIDToSpecIndexPair> detId2SpecIndex;

  bool doGroup = false;
  if (groupWS) {
    doGroup = true;
    detId2SpecIndex = createDetectorToSpectrumMapping(groupWS.get());
    inst = groupWS->getInstrument();
  }

  bool doOffsets = false;
  if (offsetsWS) {
    doOffsets = true;
    detId2SpecIndex = createDetectorToSpectrumMapping(offsetsWS.get());
    inst = offsetsWS->getInstrument();
  }

  bool doMask = false;
  if (maskWS) {
    doMask = true;
    inst = maskWS->getInstrument();
    if (!inst)
      g_log.warning() << "Mask workspace " << maskWS->getName()
                      << " has no instrument associated with."
                      << "\n";
  }

  g_log.information() << "Status: doGroup = " << doGroup
                      << " doOffsets = " << doOffsets << " doMask = " << doMask
                      << "\n";

  if (!inst || detId2SpecIndex.empty())
    throw std::invalid_argument("You must give at least one of the grouping, "
                                "offsets or masking workspaces.");

  if (getProperty("Sort Detector IDs")) {
    // Sort by detector ID
    std::sort(detId2SpecIndex.begin(), detId2SpecIndex.end(), sortByDetID);
  } else {
    // Sort by spectrum index
    std::sort(detId2SpecIndex.begin(), detId2SpecIndex.end(),
              sortBySpectrumIndex);
  }

  // Header of the file
  std::ofstream fout(calFileName.c_str());
  fout << "# Calibration file for instrument " << inst->getName()
       << " written on " << DateAndTime::getCurrentTime().toISO8601String()
       << ".\n";
  fout << "# Format: number    UDET         offset    select    group\n";

  size_t number = 0;

  for (const auto detIDandSpecNum : detId2SpecIndex) {
    const auto &detectorID = detIDandSpecNum.first;

    // Find the offset, if any
    double offset = 0.0;
    if (doOffsets)
      offset = offsetsWS->getValue(detectorID, 0.0);

    // Find the group, if any
    int64_t group = 1;
    if (doGroup)
      group = static_cast<int64_t>(groupWS->getValue(detectorID, 0.0));

    // Find the selection, if any
    int selected = 1;
    if (doMask && (maskWS->isMasked(detectorID)))
      selected = 0;

    // if(group > 0)
    fout << std::fixed << std::setw(9) << number << std::fixed << std::setw(15)
         << detectorID << std::fixed << std::setprecision(m_precision)
         << std::setw(15) << offset << std::fixed << std::setw(8) << selected
         << std::fixed << std::setw(8) << group << "\n";

    number++;
  }
}

bool SaveCalFile::sortBySpectrumIndex(const detIDToSpecIndexPair &a,
                                      const detIDToSpecIndexPair &b) {
  if (a.second != b.second) {
    return a.second < b.second;
  } else {
    // Use detector IDs as the spectrum index is identical
    return SaveCalFile::sortByDetID(a, b);
  }
}

bool SaveCalFile::sortByDetID(const detIDToSpecIndexPair &a,
                              const detIDToSpecIndexPair &b) {
  return a.first < b.first;
}

} // namespace Mantid
} // namespace DataHandling

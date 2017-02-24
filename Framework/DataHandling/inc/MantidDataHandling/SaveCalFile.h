#ifndef MANTID_DATAHANDLING_SAVECALFILE_H_
#define MANTID_DATAHANDLING_SAVECALFILE_H_

#include "MantidKernel/System.h"
#include "MantidAPI/Algorithm.h"
#include "MantidDataObjects/GroupingWorkspace.h"
#include "MantidDataObjects/MaskWorkspace.h"
#include "MantidDataObjects/OffsetsWorkspace.h"
#include "MantidAPI/MatrixWorkspace_fwd.h"

namespace Mantid {
namespace DataHandling {

/** Algorithm to save a 5-column ascii .cal file from  to 3 workspaces:
 * a GroupingWorkspace, OffsetsWorkspace and/or MaskWorkspace.
 *
 * @author
 * @date 2011-05-10 09:48:31.796980
 */
class DLLExport SaveCalFile : public API::Algorithm {
public:
  /// Algorithm's name for identification
  const std::string name() const override { return "SaveCalFile"; };
  /// Summary of algorithms purpose
  const std::string summary() const override {
    return "Saves a 5-column ASCII .cal file from up to 3 workspaces: a "
           "GroupingWorkspace, OffsetsWorkspace and/or MaskWorkspace.";
  }

  /// Algorithm's version for identification
  int version() const override { return 1; };
  /// Algorithm's category for identification
  const std::string category() const override {
    return "DataHandling\\Text;Diffraction\\DataHandling\\CalFiles";
  }

  void saveCalFile(const std::string &calFileName,
                   Mantid::DataObjects::GroupingWorkspace_sptr groupWS,
                   Mantid::DataObjects::OffsetsWorkspace_sptr offsetsWS,
                   Mantid::DataObjects::MaskWorkspace_sptr maskWS);

private:
  /// Initialise the properties
  void init() override;
  /// Run the algorithm
  void exec() override;

  /// Adds the detectorIDs and the corresponding spectrum index to a new vector
  template <typename T>
  std::vector<std::pair<Mantid::detid_t, size_t>>
  createDetectorToSpectrumMapping(const T *ws);

  /// Typedef the pair for future usage
  using detIDToSpecIndexPair = std::pair<Mantid::detid_t, size_t>;

  /// Sorts by detector ID
  static bool sortByDetID(const detIDToSpecIndexPair &a,
                          const detIDToSpecIndexPair &b);

  /// Sorts by Spectrum Index - If identical falls back to using detector ID
  static bool sortBySpectrumIndex(const detIDToSpecIndexPair &a,
                                  const detIDToSpecIndexPair &b);

  /// Offset precision
  int m_precision{7};
};

} // namespace Mantid
} // namespace DataHandling

#endif /* MANTID_DATAHANDLING_SAVECALFILE_H_ */

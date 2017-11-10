#include "MantidCrystal/SavePeaksFile.h"
#include "MantidAPI/FileProperty.h"
#include "MantidDataObjects/PeaksWorkspace.h"

namespace Mantid {
namespace Crystal {

// Register the algorithm into the AlgorithmFactory
// DECLARE_ALGORITHM(SavePeaksFile)

using namespace Mantid::Kernel;
using namespace Mantid::API;
using namespace Mantid::DataObjects;

//----------------------------------------------------------------------------------------------
/** Initialize the algorithm's properties.
 */
void SavePeaksFile::init() {
  declareProperty(make_unique<WorkspaceProperty<Workspace>>(
                      "InputWorkspace", "", Direction::Input),
                  "An input PeaksWorkspace.");

  declareProperty(
      make_unique<FileProperty>("Filename", "", FileProperty::Save, ".peaks"),
      "Path to an ISAW-style .peaks filename.");
}

//----------------------------------------------------------------------------------------------
/** Execute the algorithm.
 */
void SavePeaksFile::exec() {
  // Retrieve the workspace
  Workspace_sptr ws_in = getProperty("InputWorkspace");
  PeaksWorkspace_sptr ws = boost::dynamic_pointer_cast<PeaksWorkspace>(ws_in);
  if (!ws)
    throw std::invalid_argument(
        "Workspace given as input is invalid or not a PeaksWorkspace.");

  // std::string filename = getPropertyValue("Filename");

  throw std::runtime_error("NOT YET IMPLEMENTED."); // TODO!
                                                    // ws->write(filename);
}

} // namespace Mantid
} // namespace Crystal

#include "MantidDataHandling/LoadShape.h"

#include "MantidAPI/AnalysisDataService.h"
#include "MantidAPI/FileProperty.h"
#include "MantidAPI/InstrumentValidator.h"
#include "MantidAPI/WorkspaceFactory.h"
#include "MantidAPI/MatrixWorkspace.h"
#include "MantidAPI/MatrixWorkspace_fwd.h"
#include "MantidAPI/Sample.h"

#include "MantidGeometry/Instrument.h"
#include "MantidKernel/Material.h"
#include "MantidKernel/CompositeValidator.h"
#include "MantidKernel/EnabledWhenProperty.h"
#include "MantidKernel/Exception.h"

#include <Poco/File.h>

namespace Mantid {
namespace DataHandling {
// Register the algorithm into the algorithm factory
DECLARE_ALGORITHM(LoadShape)

using namespace Kernel;
using namespace API;
using namespace Geometry;

void LoadShape::init() {
  auto wsValidator = boost::make_shared<CompositeValidator>();
  wsValidator->add<API::InstrumentValidator>();

  // input workspace
  declareProperty(
      make_unique<WorkspaceProperty<>>("InputWorkspace", "", Direction::Input,
                                       wsValidator),
      "The name of the workspace containing the instrument to add the shape");

  // shape file
  const std::vector<std::string> extensions{ ".stl" };
  declareProperty(
       make_unique<FileProperty>(
      "Filename", "", FileProperty::Load, extensions),
      "The name of the file containing the shape. "
      "Extension must be .stl");

  // Output workspace
  declareProperty(
       make_unique<WorkspaceProperty<>>(
       "OutputWorkspace", "", Direction::Output),
       "The name of the workspace that will be same as"
       "the input workspace but with shape added to it");

}

/**
* Return the confidence with with this algorithm can load the file
* @param descriptor A descriptor for the file
* @returns An integer specifying the confidence level. 0 indicates it will not
* be used
*/
int LoadShape::confidence(Kernel::FileDescriptor &descriptor) const {
  const std::string &filePath = descriptor.filename();
  const size_t filenameLength = filePath.size();

  // Avoid some known file types that have different loaders
  int confidence(0);
  if (filePath.compare(filenameLength - 4, 4, ".stl") == 0 ) {
    confidence = 90;
  }
  return confidence;
}

void LoadShape::exec() {

  MatrixWorkspace_const_sptr inputWS = getProperty("InputWorkspace");
  MatrixWorkspace_sptr outputWS = getProperty("OutputWorkspace");

  if (inputWS != outputWS) {
    outputWS = inputWS->clone();
  }

  std::string filename = getProperty("Filename");
  std::ifstream file(filename.c_str());
  if (!file) {
    g_log.error("Unable to open file: " + filename);
    throw Exception::FileError("Unable to open file: ", filename);
  }

  std::string solidName = "";
  boost::shared_ptr<MeshObject> shape = nullptr;  
  try {
    shape = readSTLSolid(file, solidName);
  }
  catch (std::exception &) {
    throw Exception::FileError("Failed to recognize this file as a valid STL file: ", filename);
  }

  // Put shape into sample.
  Sample &sample = outputWS->mutableSample();
  sample.setShape(shape);

}

std::unique_ptr<Geometry::MeshObject> LoadShape::readSTLSolid(std::ifstream &file, std::string &name) {
  // Read Solid name
  // We expect line after trimming to be "solid "+name.
  std::string line;
  if (getline(file, line)) {
    boost::trim(line);
    if (line.size() < 5 || line.substr(0, 5) != "solid") {
      throw std::runtime_error("Expected start of solid");
    }
    else {
      name = line.substr(6, std::string::npos);
    }
    // Read Solid shape
    return readSTLMeshObject(file);
  }
  return nullptr;
}

std::unique_ptr<MeshObject> LoadShape::readSTLMeshObject(std::ifstream& file) {
  std::vector<uint16_t> triangleIndices;
  std::vector<V3D> vertices;
  V3D t1, t2, t3;

  while (readSTLTriangle(file, t1, t2, t3)) {
    triangleIndices.push_back(addSTLVertex(t1, vertices));
    triangleIndices.push_back(addSTLVertex(t2, vertices));
    triangleIndices.push_back(addSTLVertex(t3, vertices));
  }
  // Use efficient constructor of MeshObject
  std::unique_ptr<MeshObject> retVal = std::unique_ptr<MeshObject>(
    new MeshObject(std::move(triangleIndices), std::move(vertices),
      Mantid::Kernel::Material()));
  return retVal;
}

/* Reads triangle for STL file and returns true if triangle is found */
bool LoadShape::readSTLTriangle(std::ifstream &file, V3D &v1, V3D &v2, V3D &v3) {

  std::string line;
  if (readSTLLine(file, "facet") && readSTLLine(file, "outer loop")) {
      bool ok = (
        readSTLVertex(file, v1) &&
        readSTLVertex(file, v2) &&
        readSTLVertex(file, v3));
      if (!ok) {
        throw std::runtime_error("Error on reading STL triangle");
      }
  } else {
    return false; // End of file
  }
  return readSTLLine(file, "endloop") && readSTLLine(file, "endfacet");
}

/* Reads vertex from STL file and returns true if vertex is found */
bool LoadShape::readSTLVertex(std::ifstream &file, V3D &vertex) {
  std::string line;
  if (getline(file, line)) {
    boost::trim(line);
    std::vector<std::string> tokens;
    boost::split(tokens, line, boost::is_any_of(" "), boost::token_compress_on);
    if (tokens.size() == 4 && tokens[0] == "vertex") {
      vertex.setX(boost::lexical_cast<double>(tokens[1]));
      vertex.setY(boost::lexical_cast<double>(tokens[2]));
      vertex.setZ(boost::lexical_cast<double>(tokens[3]));
      return true;
    } else {
      throw std::runtime_error("Error on reading STL vertex");
    }
  }
  return false;
}

// Read, check and ignore line in STL file. Return true if line is read
bool LoadShape::readSTLLine(std::ifstream &file, std::string const &type) {
  std::string line;
  if (getline(file, line)) {
    boost::trim(line);
    if (line.size() < type.size() || line.substr(0, type.size()) != type) {
      // Before throwing, check for endsolid statment
      std::string type2 = "endsolid";
      if (line.size() < type2.size() || line.substr(0, type2.size()) != type2) {
        throw std::runtime_error("Expected STL line begining with " + type + " or "+ type2);
      }
      else {
        return false; // ends reading at endsolid
      }
    }
    return true; // expected line read, then ignored
  }
  else {
    return false; // end of file
  }
}

// Adds vertex to list if distinct and returns index to vertex added or equal
uint16_t LoadShape::addSTLVertex(V3D &vertex, std::vector<V3D> &vertices) {
  for (uint16_t i = 0; i < vertices.size(); ++i) {
    if (areEqualVertices(vertex, vertices[i])) {
      return i;
    }
  }
  vertices.push_back(vertex);
  uint16_t index = (uint16_t) vertices.size() - 1;
  if (index != vertices.size() - 1) {
    throw std::runtime_error("Too many vertices in solid");
  }
  return index;
}

} // end DataHandling namespace
} // end MantidNamespace

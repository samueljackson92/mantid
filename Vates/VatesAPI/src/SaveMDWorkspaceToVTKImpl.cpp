#include "MantidVatesAPI/SaveMDWorkspaceToVTKImpl.h"
#include "MantidVatesAPI/ADSWorkspaceProvider.h"
#include "MantidVatesAPI/Normalization.h"

#include "MantidVatesAPI/NoThresholdRange.h"
#include "MantidVatesAPI/IgnoreZerosThresholdRange.h"

#include "MantidVatesAPI/MDLoadingViewSimple.h"
#include "MantidVatesAPI/MDEWInMemoryLoadingPresenter.h"
#include "MantidVatesAPI/MDHWInMemoryLoadingPresenter.h"
#include "MantidVatesAPI/ProgressAction.h"
#include "MantidVatesAPI/PresenterUtilities.h"
#include "MantidVatesAPI/SingleWorkspaceProvider.h"

#include "MantidVatesAPI/vtkMDHistoLineFactory.h"
#include "MantidVatesAPI/vtkMDHistoQuadFactory.h"
#include "MantidVatesAPI/vtkMDHistoHexFactory.h"
#include "MantidVatesAPI/vtkMDHistoHex4DFactory.h"

#include "MantidVatesAPI/vtkMD0DFactory.h"
#include "MantidVatesAPI/vtkMDHexFactory.h"
#include "MantidVatesAPI/vtkMDQuadFactory.h"
#include "MantidVatesAPI/vtkMDLineFactory.h"

#include "MantidGeometry/MDGeometry/IMDDimension.h"

#include <vtkSmartPointer.h>
#include <vtkXMLStructuredGridWriter.h>
#include <vtkXMLUnstructuredGridWriter.h>

#include "MantidAPI/IMDEventWorkspace.h"
#include "MantidAPI/IMDHistoWorkspace.h"

#include "MantidKernel/make_unique.h"
#include <memory>
#include <boost/make_shared.hpp>

namespace {
class NullProgressAction : public Mantid::VATES::ProgressAction
{
  virtual void eventRaised(double)
  {
  }
};

bool has_suffix(const std::string &str, const std::string &suffix)
{
    return str.size() >= suffix.size() &&
           str.compare(str.size() - suffix.size(), suffix.size(), suffix) == 0;
}

}


namespace Mantid {
namespace VATES {

const std::string SaveMDWorkspaceToVTKImpl::structuredGridExtension = "vts";
const std::string SaveMDWorkspaceToVTKImpl::unstructuredGridExtension = "vtu";

SaveMDWorkspaceToVTKImpl::SaveMDWorkspaceToVTKImpl() {
  setupMembers();
}

/**
 * Save an MDHisto workspace to a vts file.
 * @param histoWS: the histo workspace which is to be saved.
 * @param filename: the name of the file to which the workspace is to be saved.
 * @param normalization: the visual normalization option
 * @param thresholdRange: a plolicy for the threshold range
 * @param recursionDepth: the recursion depth for MDEvent Workspaces determines from which level data should be displayed
 */
void SaveMDWorkspaceToVTKImpl::saveMDWorkspace(Mantid::API::IMDWorkspace_sptr workspace,
  std::string filename, VisualNormalization normalization, ThresholdRange_scptr thresholdRange, int recursionDepth) const {
  auto isHistoWorkspace = boost::dynamic_pointer_cast<Mantid::API::IMDHistoWorkspace>(workspace) != nullptr;
  auto fullFilename = getFullFilename(filename, isHistoWorkspace);

  // Define a time slice.
  auto time = selectTimeSliceValue(workspace);

  // Choose settings based on workspace type

  std::unique_ptr<MDLoadingPresenter> presenter = nullptr;
  auto view = Kernel::make_unique<Mantid::VATES::MDLoadingViewSimple>();
  std::unique_ptr<vtkDataSetFactory> factoryChain = nullptr;
  auto workspaceProvider  =  Mantid::Kernel::make_unique<SingleWorkspaceProvider>(workspace);

  if (isHistoWorkspace) {
      presenter = createInMemoryPresenter<MDHWInMemoryLoadingPresenter>(std::move(view), workspace, std::move(workspaceProvider));
      factoryChain = createFactoryChain5Factories<vtkMDHistoHex4DFactory, vtkMDHistoHexFactory,
                                               vtkMDHistoQuadFactory, vtkMDHistoLineFactory,
                                               vtkMD0DFactory>(thresholdRange, normalization, time);
  } else {
      view->setRecursionDepth(recursionDepth);
      presenter = createInMemoryPresenter<MDEWInMemoryLoadingPresenter>(std::move(view), workspace, std::move(workspaceProvider));
      factoryChain = createFactoryChain4Factories<vtkMDHexFactory, vtkMDQuadFactory, vtkMDLineFactory,
                                               vtkMD0DFactory>(thresholdRange, normalization, time);
  }

  // Create the vtk data
  NullProgressAction nullProgressA;
  NullProgressAction nullProgressB;
  auto dataSet = presenter->execute(factoryChain.get(), nullProgressA, nullProgressB);

  // Do an orthogonal correction
  dataSet = getDataSetWithOrthogonalCorrection(dataSet, presenter.get(), isHistoWorkspace);

  // Write the data to the file
  vtkSmartPointer<vtkXMLWriter> writer  = getXMLWriter(isHistoWorkspace);
  auto writeSuccessFlag = writeDataSetToVTKFile(writer, dataSet, fullFilename);
  if (!writeSuccessFlag) {
    throw std::runtime_error("SaveMDWorkspaceToVTK: VTK could not write your data set to a file.");
  }
}


/**
 * Write an unstructured grid or structured grid to a vtk file.
 * @param writer: a vtk xml writer
 * @param dataSet: the data set which is to be saved out
 * @param filename: the file name
 * @returns a vtk error flag
 */
int SaveMDWorkspaceToVTKImpl::writeDataSetToVTKFile(vtkXMLWriter* writer, vtkDataSet* dataSet, std::string filename) const {
  writer->SetFileName(filename.c_str());
  writer->SetInputData(dataSet);
  return writer->Write();
}

/**
 * Get all allowed normalizations
 * @returns all allowed normalization options as strings
 */
std::vector<std::string> SaveMDWorkspaceToVTKImpl::getAllowedNormalizationsInStringRepresentation() const {
  std::vector<std::string> normalizations;
  for (auto it = m_normalizations.begin(); it != m_normalizations.end(); ++it) {
    normalizations.push_back(it->first);
  }

  return normalizations;
}

VisualNormalization SaveMDWorkspaceToVTKImpl::translateStringToVisualNormalization(const std::string normalization) const {
  return m_normalizations.at(normalization);
}

void SaveMDWorkspaceToVTKImpl::setupMembers() {
  m_normalizations.insert(std::make_pair("AutoSelect", VisualNormalization::AutoSelect));
  m_normalizations.insert(std::make_pair("NoNormalization", VisualNormalization::NoNormalization));
  m_normalizations.insert(std::make_pair("NumEventsNormalization", VisualNormalization::NumEventsNormalization));
  m_normalizations.insert(std::make_pair("VolumeNormalization", VisualNormalization::VolumeNormalization));

  m_thresholds.push_back("IgnoreZerosThresholdRange");
  m_thresholds.push_back("NoThresholdRange");
}

std::vector<std::string> SaveMDWorkspaceToVTKImpl::getAllowedThresholdsInStringRepresentation() const {
  return m_thresholds;
}


ThresholdRange_scptr SaveMDWorkspaceToVTKImpl::translateStringToThresholdRange(const std::string thresholdRange) const {
  if (thresholdRange == m_thresholds[0]) {
      return boost::make_shared<IgnoreZerosThresholdRange>();
  } else if (thresholdRange == m_thresholds[1]) {
      return boost::make_shared<NoThresholdRange>();
  } else {
    throw std::runtime_error("SaveMDWorkspaceToVTK: The selected threshold range seems to be incorrect.");
  }
}


/**
 * Returns a time for a time slice
 * @param workspace: the workspace
 * @return either the first time entry in case of a 4D workspace or else 0.0
 */
double SaveMDWorkspaceToVTKImpl::selectTimeSliceValue(Mantid::API::IMDWorkspace_sptr workspace) const {
  double time = 0.0;
  if (is4DWorkspace(workspace)) {
      auto timeLikeDimension = workspace->getDimension(3);
      time = static_cast<double>(timeLikeDimension->getMinimum());
  }
  return time;
}

bool SaveMDWorkspaceToVTKImpl::is4DWorkspace(Mantid::API::IMDWorkspace_sptr workspace) const {
  auto actualNonIntegratedDimensionality = workspace->getNonIntegratedDimensions().size();
  const size_t dimensionsWithTime = 4;
  return actualNonIntegratedDimensionality == dimensionsWithTime;
}

std::string SaveMDWorkspaceToVTKImpl::getFullFilename(std::string filename, bool isHistoWorkspace) const{
  auto extension = isHistoWorkspace ? structuredGridExtension : unstructuredGridExtension;
  if (!has_suffix(filename, extension)) {
      filename += ".";
      filename += extension;
  }
  return filename;
}

vtkSmartPointer<vtkXMLWriter> SaveMDWorkspaceToVTKImpl::getXMLWriter(bool isHistoWorkspace) const {
  vtkSmartPointer<vtkXMLWriter> writer;
  if (isHistoWorkspace) {
      writer = vtkSmartPointer<vtkXMLStructuredGridWriter>::New();
  } else {
      writer = vtkSmartPointer<vtkXMLUnstructuredGridWriter>::New();
  }
  return writer;
}

vtkSmartPointer<vtkDataSet> SaveMDWorkspaceToVTKImpl::getDataSetWithOrthogonalCorrection(vtkSmartPointer<vtkDataSet> dataSet, MDLoadingPresenter* presenter, bool isHistoWorkspace)  const{
  if (!isHistoWorkspace) {
    vtkSmartPointer<vtkPVClipDataSet> clipped = getClippedDataSet(dataSet);
    dataSet = clipped->GetOutput();
  }
  applyCOBMatrixSettingsToVtkDataSet(presenter, dataSet);
  presenter->setAxisLabels(dataSet);

  return dataSet;
}

}
}

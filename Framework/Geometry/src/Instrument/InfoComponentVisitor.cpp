#include "MantidGeometry/Instrument/InfoComponentVisitor.h"
#include "MantidGeometry/IComponent.h"
#include "MantidGeometry/ICompAssembly.h"
#include "MantidGeometry/IDetector.h"
#include "MantidGeometry/Instrument/ParameterMap.h"
#include "MantidKernel/EigenConversionHelpers.h"
#include "MantidKernel/make_unique.h"
#include "MantidBeamline/ComponentInfo.h"
#include "MantidBeamline/DetectorInfo.h"

#include <numeric>
#include <algorithm>
#include <boost/make_shared.hpp>

namespace Mantid {

namespace Geometry {

using namespace Mantid::Geometry;

namespace {
boost::shared_ptr<const std::unordered_map<detid_t, size_t>>
makeDetIdToIndexMap(const std::vector<detid_t> &detIds) {

  const size_t nDetIds = detIds.size();
  auto detIdToIndex = boost::make_shared<std::unordered_map<detid_t, size_t>>();
  detIdToIndex->reserve(nDetIds);
  for (size_t i = 0; i < nDetIds; ++i) {
    (*detIdToIndex)[detIds[i]] = i;
  }
  return std::move(detIdToIndex);
}

void clearPositionAndRotationParameters(ParameterMap &pmap,
                                        const IComponent &comp) {
  pmap.clearParametersByName(ParameterMap::pos(), &comp);
  pmap.clearParametersByName(ParameterMap::posx(), &comp);
  pmap.clearParametersByName(ParameterMap::posy(), &comp);
  pmap.clearParametersByName(ParameterMap::posz(), &comp);
  pmap.clearParametersByName(ParameterMap::rot(), &comp);
  pmap.clearParametersByName(ParameterMap::rotx(), &comp);
  pmap.clearParametersByName(ParameterMap::roty(), &comp);
  pmap.clearParametersByName(ParameterMap::rotz(), &comp);
}
}

InfoComponentVisitor::InfoComponentVisitor(
    std::vector<detid_t> orderedDetectorIds, ParameterMap &pmap,
        ComponentID sourceId, ComponentID sampleId
        )
    : m_componentIds(boost::make_shared<std::vector<ComponentID>>(
          orderedDetectorIds.size(), nullptr)),
      m_assemblySortedDetectorIndices(
          boost::make_shared<std::vector<size_t>>()),
      m_assemblySortedComponentIndices(
          boost::make_shared<std::vector<size_t>>()),
      m_parentComponentIndices(boost::make_shared<std::vector<size_t>>()),
      m_detectorRanges(
          boost::make_shared<std::vector<std::pair<size_t, size_t>>>()),
      m_componentRanges(
          boost::make_shared<std::vector<std::pair<size_t, size_t>>>()),
      m_componentIdToIndexMap(boost::make_shared<
          std::unordered_map<Mantid::Geometry::IComponent *, size_t>>()),
      m_detectorIdToIndexMap(makeDetIdToIndexMap(orderedDetectorIds)),
      m_orderedDetectorIds(boost::make_shared<std::vector<detid_t>>(
          std::move(orderedDetectorIds))),
      m_positions(boost::make_shared<std::vector<Eigen::Vector3d>>()),
      m_rotations(boost::make_shared<std::vector<Eigen::Quaterniond>>()),
      m_pmap(pmap),
      m_sourceId(sourceId),
      m_sampleId(sampleId)
{
  const auto nDetectors = m_orderedDetectorIds->size();
  m_assemblySortedDetectorIndices->reserve(nDetectors);  // Exact
  m_assemblySortedComponentIndices->reserve(nDetectors); // Approximation
  m_parentComponentIndices->reserve(nDetectors);         // Approximation
  // m_componentIdToIndexMap->reserve(nDetectors);          // Approximation
}

/**
 * @brief InfoComponentVisitor::registerComponentAssembly
 * @param assembly : ICompAssembly being visited
 * @return Component index of this component
 */
size_t
InfoComponentVisitor::registerComponentAssembly(const ICompAssembly &assembly) {

  std::vector<IComponent_const_sptr> assemblyChildren;
  assembly.getChildren(assemblyChildren, false /*is recursive*/);

  const size_t detectorStart = m_assemblySortedDetectorIndices->size();
  const size_t componentStart = m_assemblySortedComponentIndices->size();
  std::vector<size_t> children(assemblyChildren.size());
  for (size_t i = 0; i < assemblyChildren.size(); ++i) {
    // register everything under this assembly
    children[i] = assemblyChildren[i]->registerContents(*this);
    m_parentComponentIndices->push_back(0);
  }
  const size_t detectorStop = m_assemblySortedDetectorIndices->size();
  const size_t componentIndex = m_componentIds->size();
  m_assemblySortedComponentIndices->push_back(componentIndex);
  const size_t componentStop = m_assemblySortedComponentIndices->size();

  m_detectorRanges->emplace_back(std::make_pair(detectorStart, detectorStop));
  m_componentRanges->emplace_back(
      std::make_pair(componentStart, componentStop));

  // Record the ID -> index mapping
  (*m_componentIdToIndexMap)[assembly.getComponentID()] = componentIndex;
  // For any non-detector we extend the m_componentIds from the back
  m_componentIds->emplace_back(assembly.getComponentID());
  m_positions->emplace_back(Kernel::toVector3d(assembly.getPos()));
  m_rotations->emplace_back(Kernel::toQuaterniond(assembly.getRotation()));
  clearPositionAndRotationParameters(m_pmap, assembly);
  // Now that we know what the index of the parent is we can apply it to the
  // children
  for (const auto &child : children) {
    (*m_parentComponentIndices)[child] = componentIndex;
  }
  markAsSourceOrSample(assembly.getComponentID(), componentIndex);
  return componentIndex;
}

/**
 * @brief InfoComponentVisitor::registerGenericComponent
 * @param component : IComponent being visited
 * @return Component index of this component
 */
size_t
InfoComponentVisitor::registerGenericComponent(const IComponent &component) {
  /*
   * For a generic leaf component we extend the component ids list, but
   * the detector indexes entries will of course be empty
   */
  m_detectorRanges->emplace_back(
      std::make_pair(0, 0)); // Represents an empty range
  m_componentRanges->emplace_back(
      std::make_pair(0, 0)); // Represents an empty range
  // Record the ID -> index mapping
  const size_t componentIndex = m_componentIds->size();
  (*m_componentIdToIndexMap)[component.getComponentID()] = componentIndex;
  m_componentIds->emplace_back(component.getComponentID());
  m_positions->emplace_back(Kernel::toVector3d(component.getPos()));
  m_rotations->emplace_back(Kernel::toQuaterniond(component.getRotation()));
  m_assemblySortedComponentIndices->push_back(componentIndex);
  clearPositionAndRotationParameters(m_pmap, component);
  markAsSourceOrSample(component.getComponentID(), componentIndex);
  return componentIndex;
}

void InfoComponentVisitor::markAsSourceOrSample(ComponentID componentId, const size_t componentIndex){
  if(componentId == m_sampleId){
      m_sampleIndex = componentIndex;
  }
  else if(componentId == m_sourceId){
      m_sourceIndex = componentIndex;
  }
}

/**
 * @brief InfoComponentVisitor::registerDetector
 * @param detector : IDetector being visited
 * @return Component index of this component
 */
size_t InfoComponentVisitor::registerDetector(const IDetector &detector) {

  size_t detectorIndex = 0;
  try {
    detectorIndex = m_detectorIdToIndexMap->at(detector.getID());
  } catch (std::out_of_range &) {
    /*
     Do not register a detector with an invalid id. if we can't determine
     the index, we cannot register it in the right place!
    */
    ++m_droppedDetectors;
    return detectorIndex;
  }
  if (m_componentIds->at(detectorIndex) == nullptr) {

    /* Already allocated we just need to index into the inital front-detector
    * part of the collection.
    * 1. Guarantee on grouping detectors by type such that the first n
    * components
    * are detectors.
    * 2. Guarantee on ordering such that the
    * detectorIndex == componentIndex for all detectors.
    */
    // Record the ID -> component index mapping
    (*m_componentIdToIndexMap)[detector.getComponentID()] = detectorIndex;
    (*m_componentIds)[detectorIndex] = detector.getComponentID();
    m_assemblySortedDetectorIndices->push_back(detectorIndex);
    m_assemblySortedComponentIndices->push_back(detectorIndex);
  }
  /* Note that positions and rotations for detectors are currently
  NOT stored! These go into DetectorInfo at present. push_back works for other
  Component types because Detectors are always come first in the resultant
  component list
  forming a contiguous block.
  */
  markAsSourceOrSample(detector.getComponentID(), detectorIndex); // TODO. Optimisation. Cannot have a detector that is either source or sample. So delete this.
  return detectorIndex;
}

/**
 * @brief InfoComponentVisitor::componentDetectorRanges
 * @return index ranges into the detectorIndices vector. Gives the
 * intervals of detectors indices for non-detector components such as banks
 */
boost::shared_ptr<const std::vector<std::pair<size_t, size_t>>>
InfoComponentVisitor::componentDetectorRanges() const {
  return m_detectorRanges;
}

boost::shared_ptr<const std::vector<std::pair<size_t, size_t>>>
InfoComponentVisitor::componentChildComponentRanges() const {
  return m_componentRanges;
}

/**
 * @brief InfoComponentVisitor::detectorIndices
 * @return detector indices in the order in which they have been visited
 * thus grouped by assembly to form a contiguous range for levels of assemblies.
 */
boost::shared_ptr<const std::vector<size_t>>
InfoComponentVisitor::assemblySortedDetectorIndices() const {
  return m_assemblySortedDetectorIndices;
}

boost::shared_ptr<const std::vector<size_t>>
InfoComponentVisitor::assemblySortedComponentIndices() const {
  return m_assemblySortedComponentIndices;
}

boost::shared_ptr<const std::vector<size_t>>
InfoComponentVisitor::parentComponentIndices() const {
  return m_parentComponentIndices;
}

/**
 * @brief InfoComponentVisitor::componentIds
 * @return  component ids in the order in which they have been visited.
 * Note that the number of component ids will be >= the number of detector
 * indices
 * since all detectors are components but not all components are detectors
 */
boost::shared_ptr<const std::vector<Mantid::Geometry::ComponentID>>
InfoComponentVisitor::componentIds() const {
  return m_componentIds;
}

/**
 * @brief InfoComponentVisitor::size
 * @return The total size of the components visited.
 * This will be the same as the number of IDs.
 */
size_t InfoComponentVisitor::size() const {
  return m_componentIds->size() - m_droppedDetectors;
}

bool InfoComponentVisitor::isEmpty() const { return size() == 0; }

boost::shared_ptr<
    const std::unordered_map<Mantid::Geometry::IComponent *, size_t>>
InfoComponentVisitor::componentIdToIndexMap() const {
  return m_componentIdToIndexMap;
}

boost::shared_ptr<const std::unordered_map<detid_t, size_t>>
InfoComponentVisitor::detectorIdToIndexMap() const {
  return m_detectorIdToIndexMap;
}

std::unique_ptr<Beamline::ComponentInfo> InfoComponentVisitor::componentInfo(
    Beamline::DetectorInfo *const detectorInfo) const {
  return Kernel::make_unique<Mantid::Beamline::ComponentInfo>(
      m_assemblySortedDetectorIndices, m_detectorRanges,
      m_assemblySortedComponentIndices, m_componentRanges,
      m_parentComponentIndices, m_positions, m_rotations, detectorInfo);
}

boost::shared_ptr<std::vector<detid_t>>
InfoComponentVisitor::detectorIds() const {
  return m_orderedDetectorIds;
}

boost::shared_ptr<std::vector<Eigen::Vector3d>>
InfoComponentVisitor::positions() const {
  return m_positions;
}

boost::shared_ptr<std::vector<Eigen::Quaterniond>>
InfoComponentVisitor::rotations() const {
    return m_rotations;
}

size_t InfoComponentVisitor::sampleIndex() const
{
    return m_sampleIndex;
}

size_t InfoComponentVisitor::sourceIndex() const
{
    return m_sourceIndex;
}

} // namespace Geometry
} // namespace Mantid
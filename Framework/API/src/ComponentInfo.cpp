#include "MantidAPI/ComponentInfo.h"
#include "MantidGeometry/IComponent.h"
#include "MantidBeamline/ComponentInfo.h"
#include <boost/make_shared.hpp>
#include <exception>
#include <string>
#include <boost/make_shared.hpp>
#include <sstream>

namespace Mantid {
namespace API {

/**
 * Constructor
 * @param componentInfo : Beamline wrapped ComponentInfo
 * @param componentIds : Component Ids ordered by component index
 */
ComponentInfo::ComponentInfo(const Beamline::ComponentInfo &componentInfo,
                             std::vector<Geometry::ComponentID> &&componentIds)
    : m_componentInfo(componentInfo),
      m_componentIds(
          boost::make_shared<std::vector<Geometry::ComponentID>>(componentIds)),
      m_compIDToIndex(boost::make_shared<
          std::unordered_map<Geometry::IComponent *, size_t>>()) {

  /*
   * Ideally we would check here that componentIds.size() ==
   * m_componentInfo.size().
   * Currently that check would break too much in Mantid.
   */

  for (size_t i = 0; i < m_componentInfo.size(); ++i) {
    (*m_compIDToIndex)[(*m_componentIds)[i]] = i;
  }
}

std::vector<size_t>
ComponentInfo::detectorIndices(size_t componentIndex) const {
  return m_componentInfo.detectorIndices(componentIndex);
}

size_t ComponentInfo::size() const { return m_componentInfo.size(); }

Eigen::Vector3d ComponentInfo::position(const size_t componentIndex) const {
  return m_componentInfo.position(componentIndex);
}

Eigen::Quaterniond ComponentInfo::rotation(const size_t componentIndex) const {
  return m_componentInfo.rotation(componentIndex);
}

size_t ComponentInfo::indexOf(Geometry::IComponent *id) const {
  return m_compIDToIndex->at(id);
}

} // namespace API
} // namespace Mantid
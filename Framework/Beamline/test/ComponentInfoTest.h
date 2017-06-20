#ifndef MANTID_BEAMLINE_COMPONENTINFOTEST_H_
#define MANTID_BEAMLINE_COMPONENTINFOTEST_H_

#include <cxxtest/TestSuite.h>

#include "MantidBeamline/ComponentInfo.h"
#include "MantidBeamline/DetectorInfo.h"
#include <boost/make_shared.hpp>
#include <tuple>
#include <Eigen/Geometry>

using namespace Mantid::Beamline;

namespace {

std::tuple<ComponentInfo, std::vector<Eigen::Vector3d>,
           std::vector<Eigen::Quaterniond>, std::vector<Eigen::Vector3d>,
           std::vector<Eigen::Quaterniond>, boost::shared_ptr<DetectorInfo>>
makeTreeExampleAndReturnGeometricArguments() {

  /*
         |
   ------------
   |         | 1
  -------
  | 0  | 2
  */

  // Set detectors at different positions
  std::vector<Eigen::Vector3d> detPositions;
  detPositions.emplace_back(1, -1, 0);
  detPositions.emplace_back(2, -1, 0);
  detPositions.emplace_back(3, -1, 0);
  // Set all Detectors rotated 45 degrees around Y
  std::vector<Eigen::Quaterniond> detRotations(
      3, Eigen::Quaterniond(
             Eigen::AngleAxisd(M_PI / 4, Eigen::Vector3d::UnitY())));
  auto detectorInfo =
      boost::make_shared<DetectorInfo>(detPositions, detRotations);
  auto bankSortedDetectorIndices =
      boost::make_shared<const std::vector<size_t>>(
          std::vector<size_t>{0, 2, 1});
  auto bankSortedComponentIndices =
      boost::make_shared<const std::vector<size_t>>(
          std::vector<size_t>{0, 1, 3, 2, 4});
  auto parentIndices = boost::make_shared<const std::vector<size_t>>(
      std::vector<size_t>{3, 3, 4, 4});

  std::vector<std::pair<size_t, size_t>> detectorRanges;
  detectorRanges.push_back(
      std::make_pair(0, 2)); // sub-assembly (registered first)
  detectorRanges.push_back(
      std::make_pair(0, 3)); // instrument-assembly (with 3 detectors)

  std::vector<std::pair<size_t, size_t>> componentRanges;
  componentRanges.push_back(
      std::make_pair(0, 3)); // sub-assembly (contains two detectors and self)
  componentRanges.push_back(std::make_pair(
      0, 5)); // instrument assembly (with 4 sub-components and self)

  // Set non-detectors at different positions
  auto compPositions = boost::make_shared<std::vector<Eigen::Vector3d>>();
  compPositions->emplace_back(1, 0, 0);
  compPositions->emplace_back(1, -0.5, 0);

  // Set non-detectors at different rotations
  auto compRotations = boost::make_shared<std::vector<Eigen::Quaterniond>>();
  compRotations->emplace_back(Eigen::AngleAxisd(0, Eigen::Vector3d::UnitZ()));
  compRotations->emplace_back(Eigen::AngleAxisd(0, Eigen::Vector3d::UnitZ()));

  return std::make_tuple(
      ComponentInfo(
          bankSortedDetectorIndices,
          boost::make_shared<const std::vector<std::pair<size_t, size_t>>>(
              detectorRanges),
          bankSortedComponentIndices,
          boost::make_shared<const std::vector<std::pair<size_t, size_t>>>(
              componentRanges),
          parentIndices, compPositions, compRotations, detectorInfo.get()),
      detPositions, detRotations, *compPositions, *compRotations, detectorInfo);
}

std::tuple<ComponentInfo, boost::shared_ptr<DetectorInfo>> makeTreeExample() {
  /*
   Detectors are marked with detector indices below.
   There are 3 detectors.
   There are 2 assemblies, including the root

         |
   ------------
   |         | 1
  -------
  | 0  | 2
  */

  std::vector<Eigen::Vector3d> detPositions(3);
  std::vector<Eigen::Quaterniond> detRotations(3);
  auto bankSortedDetectorIndices =
      boost::make_shared<const std::vector<size_t>>(
          std::vector<size_t>{0, 2, 1});
  auto bankSortedComponentIndices =
      boost::make_shared<const std::vector<size_t>>(
          std::vector<size_t>{0, 2, 3, 1, 4});
  auto parentIndices = boost::make_shared<const std::vector<size_t>>(
      std::vector<size_t>{3, 3, 4, 4});
  std::vector<std::pair<size_t, size_t>> detectorRanges;
  detectorRanges.push_back(std::make_pair(0, 2));
  detectorRanges.push_back(std::make_pair(0, 3));

  std::vector<std::pair<size_t, size_t>> componentRanges;
  componentRanges.push_back(
      std::make_pair(0, 3)); // sub-assembly (contains two detectors and self)
  componentRanges.push_back(std::make_pair(
      0, 5)); // instrument assembly (with 4 sub-components and self)

  auto positions = boost::make_shared<std::vector<Eigen::Vector3d>>(
      2); // 2 positions provided. 2 non-detectors
  auto rotations = boost::make_shared<std::vector<Eigen::Quaterniond>>(
      2); // 2 rotations provided. 2 non-detectors

  auto detectorInfo =
      boost::make_shared<DetectorInfo>(detPositions, detRotations);
  return std::make_tuple(
      ComponentInfo(
          bankSortedDetectorIndices,
          boost::make_shared<const std::vector<std::pair<size_t, size_t>>>(
              detectorRanges),
          bankSortedComponentIndices,
          boost::make_shared<const std::vector<std::pair<size_t, size_t>>>(
              componentRanges),
          parentIndices, positions, rotations, detectorInfo.get()),
      detectorInfo);
}
}

class ComponentInfoTest : public CxxTest::TestSuite {
public:
  // This pair of boilerplate methods prevent the suite being created statically
  // This means the constructor isn't called when running other tests
  static ComponentInfoTest *createSuite() { return new ComponentInfoTest(); }
  static void destroySuite(ComponentInfoTest *suite) { delete suite; }

  void test_size() {
    /*
     Imitate an instrument with 3 detectors and nothing more.
    */
    auto infos = makeTreeExample();
    auto compInfo = std::get<0>(infos);

    TS_ASSERT_EQUALS(compInfo.size(), 5);
  }

  void
  test_constructor_throws_if_size_mismatch_between_detector_indices_and_detectorinfo() {
    /*
     Imitate an instrument with 3 detectors and nothing more.
    */
    auto bankSortedDetectorIndices =
        boost::make_shared<const std::vector<size_t>>(
            std::vector<size_t>{0, 1, 2});
    auto bankSortedComponentIndices =
        boost::make_shared<const std::vector<size_t>>(
            std::vector<size_t>{0, 1, 2});
    auto parentIndices = boost::make_shared<const std::vector<size_t>>(
        std::vector<size_t>{9, 9, 9}); // These indices are invalid, but that's
                                       // ok as not being tested here
    auto detectorRanges =
        boost::make_shared<const std::vector<std::pair<size_t, size_t>>>();
    auto componentRanges =
        boost::make_shared<const std::vector<std::pair<size_t, size_t>>>(
            std::vector<std::pair<size_t, size_t>>{});
    auto positions = boost::make_shared<std::vector<Eigen::Vector3d>>();
    auto rotations = boost::make_shared<std::vector<Eigen::Quaterniond>>();

    DetectorInfo detectorInfo; // Detector info size 0
    TS_ASSERT_THROWS(ComponentInfo(bankSortedDetectorIndices, detectorRanges,
                                   bankSortedComponentIndices, componentRanges,
                                   parentIndices, positions, rotations,
                                   &detectorInfo),
                     std::invalid_argument &);
  }

  void test_throw_if_positions_rotation_inputs_different_sizes() {
    auto detectorsInSubtree = boost::make_shared<
        const std::vector<size_t>>(); // No detector indices in this example!

    auto bankSortedComponentIndices =
        boost::make_shared<const std::vector<size_t>>(std::vector<size_t>{0});
    auto parentIndices = boost::make_shared<const std::vector<size_t>>(
        std::vector<size_t>{9, 9, 9}); // These indices are invalid, but that's
                                       // ok as not being tested here
    auto innerDetectorRanges = std::vector<std::pair<size_t, size_t>>{
        {0, 0}}; // One component with no detectors
    auto detectorRanges =
        boost::make_shared<const std::vector<std::pair<size_t, size_t>>>(
            std::move(innerDetectorRanges));

    auto innerComponentRanges = std::vector<std::pair<size_t, size_t>>{
        {0, 0}}; // One component with no sub-components
    auto componentRanges =
        boost::make_shared<const std::vector<std::pair<size_t, size_t>>>(
            std::move(innerComponentRanges));
    auto positions = boost::make_shared<std::vector<Eigen::Vector3d>>(
        1); // 1 position provided
    auto rotations = boost::make_shared<std::vector<Eigen::Quaterniond>>(
        0); // 0 rotations provided

    DetectorInfo detectorInfo;
    TS_ASSERT_THROWS(ComponentInfo(detectorsInSubtree, detectorRanges,
                                   bankSortedComponentIndices, componentRanges,
                                   parentIndices, positions, rotations,
                                   &detectorInfo),
                     std::invalid_argument &);
  }

  void test_throw_if_positions_and_rotations_not_same_size_as_detectorRanges() {
    /*
     * Positions are rotations are only currently stored for non-detector
     * components
     * We should have as many detectorRanges as we have non-detector components
     * too.
     * All vectors should be the same size.
     */
    auto detectorsInSubtree = boost::make_shared<
        const std::vector<size_t>>(); // No detector indices in this example!

    auto componentsInSubtree =
        boost::make_shared<const std::vector<size_t>>(std::vector<size_t>{0});

    auto detectorRanges = boost::make_shared<
        const std::vector<std::pair<size_t, size_t>>>(); // Empty detectorRanges

    auto parentIndices = boost::make_shared<const std::vector<size_t>>(
        std::vector<size_t>{9, 9, 9}); // These indices are invalid, but that's
                                       // ok as not being tested here
    auto positions = boost::make_shared<std::vector<Eigen::Vector3d>>(
        1); // 1 position provided
    auto rotations = boost::make_shared<std::vector<Eigen::Quaterniond>>(
        1); // 1 rotation provided

    // Only one component. So single empty component range.
    auto componentRanges =
        boost::make_shared<const std::vector<std::pair<size_t, size_t>>>(
            std::vector<std::pair<size_t, size_t>>{{0, 0}});

    DetectorInfo detectorInfo; // Empty DetectorInfo;
    TS_ASSERT_THROWS(ComponentInfo(detectorsInSubtree, detectorRanges,
                                   componentsInSubtree, componentRanges,
                                   parentIndices, positions, rotations,
                                   &detectorInfo),
                     std::invalid_argument &);
  }

  void test_read_positions_rotations() {

    auto allOutputs = makeTreeExampleAndReturnGeometricArguments();

    // Resulting ComponentInfo
    ComponentInfo info = std::get<0>(allOutputs);
    // Arguments to ComponentInfo for geometric aspects
    std::vector<Eigen::Vector3d> detPositions = std::get<1>(allOutputs);
    std::vector<Eigen::Quaterniond> detRotations = std::get<2>(allOutputs);
    std::vector<Eigen::Vector3d> compPositions = std::get<3>(allOutputs);
    std::vector<Eigen::Quaterniond> compRotations = std::get<4>(allOutputs);

    /*
     * Remember. We have 3 detectors. So component index 3 corresponds to
     * position index 0 in the input vector since we don't input positions for
     * detectors via ComponentInfo
     * constructor.
     */
    TS_ASSERT(info.position(3).isApprox(compPositions.at(0)));
    TS_ASSERT(info.position(4).isApprox(compPositions.at(1)));
    TS_ASSERT(info.rotation(3).isApprox(compRotations.at(0)));
    TS_ASSERT(info.rotation(4).isApprox(compRotations.at(1)));

    TS_ASSERT(info.position(0).isApprox(detPositions.at(0)));
    TS_ASSERT(info.position(1).isApprox(detPositions.at(1)));
    TS_ASSERT(info.position(2).isApprox(detPositions.at(2)));
    TS_ASSERT(info.rotation(0).isApprox(detRotations.at(0)));
    TS_ASSERT(info.rotation(1).isApprox(detRotations.at(1)));
    TS_ASSERT(info.rotation(2).isApprox(detRotations.at(2)));
  }

  void test_write_positions() {

    auto allOutputs = makeTreeExampleAndReturnGeometricArguments();

    // Resulting ComponentInfo
    ComponentInfo info = std::get<0>(allOutputs);
    // Arguments to ComponentInfo for geometric aspects
    std::vector<Eigen::Vector3d> originalDetPositions = std::get<1>(allOutputs);
    std::vector<Eigen::Quaterniond> originalDetRotations =
        std::get<2>(allOutputs);
    std::vector<Eigen::Vector3d> originalCompPositions =
        std::get<3>(allOutputs);
    std::vector<Eigen::Quaterniond> originalCompRotations =
        std::get<4>(allOutputs);

    // Change the position of the root.

    Eigen::Vector3d rootDestination{60, 0, 0};
    const size_t rootIndex = 4;

    const auto rootOriginalPosition = info.position(rootIndex);
    info.setPosition(rootIndex, rootDestination);
    TS_ASSERT(info.position(rootIndex).isApprox(rootDestination));

    const auto offset = rootDestination - rootOriginalPosition;
    /*
     * Remember. We have 3 detectors. So component index 3 corresponds to
     * position
     * index 0 since we don't input positions for detectors via ComponentInfo
     * constructor.
     */
    TS_ASSERT(info.position(3).isApprox(originalCompPositions.at(0) + offset));
    TS_ASSERT(info.position(4).isApprox(originalCompPositions.at(1) + offset));
    TS_ASSERT(info.rotation(3).isApprox(originalCompRotations.at(0)));
    TS_ASSERT(info.rotation(4).isApprox(originalCompRotations.at(1)));

    TS_ASSERT(info.position(0).isApprox(originalDetPositions.at(0) + offset));
    TS_ASSERT(info.position(1).isApprox(originalDetPositions.at(1) + offset));
    TS_ASSERT(info.position(2).isApprox(originalDetPositions.at(2) + offset));
    TS_ASSERT(info.rotation(0).isApprox(originalDetRotations.at(0)));
    TS_ASSERT(info.rotation(1).isApprox(originalDetRotations.at(1)));
    TS_ASSERT(info.rotation(2).isApprox(originalDetRotations.at(2)));
  }

  void test_write_rotation() {
    using namespace Eigen;
    auto allOutputs = makeTreeExampleAndReturnGeometricArguments();

    // Resulting ComponentInfo
    ComponentInfo info = std::get<0>(allOutputs);
    // Arguments to ComponentInfo for geometric aspects

    const size_t rootIndex = 4;
    const size_t detectorIndex = 1;
    const auto theta = M_PI / 2;      // 90 degree rotation
    Eigen::Vector3d axis = {0, 1, 0}; // rotate around y axis
    const auto center =
        info.position(rootIndex); // rotate around target component center.

    const auto transform = Translation3d(center) * AngleAxisd(theta, axis) *
                           Translation3d(-center);

    // Define new rotation
    const Quaterniond requestedRotation(transform.rotation());
    // Detector original rotation
    const auto detOriginalRotation = info.rotation(detectorIndex);

    // Perform 90 rotation of root
    info.setRotation(rootIndex, requestedRotation);

    // Fetch root rotation
    auto actualRootRotation = info.rotation(rootIndex);
    TSM_ASSERT("Rotations should exactly match as we are overwriting with an "
               "abs rotation",
               actualRootRotation.isApprox(requestedRotation));
    TSM_ASSERT_DELTA("Acutal rotation should be 90 deg around y",
                     std::asin(actualRootRotation.y()) * 2, theta, 1e-4);

    auto actualDetRotation = info.rotation(detectorIndex);
    TSM_ASSERT_DELTA("Detector rotation should be accumulation existing 45 + "
                     "new 90 rotation",
                     std::asin(actualDetRotation.y()) * 2,
                     theta + std::asin(detOriginalRotation.y()) * 2, 1e-4);
  }

  void test_write_rotation_updates_positions_correctly() {
    using namespace Eigen;
    auto allOutputs = makeTreeExampleAndReturnGeometricArguments();

    // Resulting ComponentInfo
    ComponentInfo info = std::get<0>(allOutputs);
    // Arguments to ComponentInfo for geometric aspects

    const size_t rootIndex = 4;
    const size_t detectorIndex = 1;
    const auto theta = M_PI / 2;                  // 90 degree rotation
    Eigen::Vector3d axis = {0, 1, 0};             // rotate around y axis
    const auto center = info.position(rootIndex); // rotate around root center.

    const auto transform = Translation3d(center) * AngleAxisd(theta, axis) *
                           Translation3d(-center);

    // Just the rotation part.
    const Quaterniond rootRotation(transform.rotation());

    const auto rootOriginalPosition = info.position(rootIndex);
    // Perform rotation
    info.setRotation(rootIndex, rootRotation);
    const auto rootUpdatedPosition = info.position(rootIndex);
    const auto detector2UpdatedPosition = info.position(detectorIndex);
    TSM_ASSERT("Rotate root around origin = root centre. It should not move!",
               rootOriginalPosition.isApprox(rootUpdatedPosition));

    /* Detector 2
     * originally at {2, -1, 0}. Rotated 90 deg around {0, 1, 0} with centre {1,
     *0, 0} should
     * put it exactly at {1, -1, -1,}
     *
     *     view down y.
     *      z
     *      ^
     *      |
     *      |--> x
     *
     * before rotation:
     *
     *      p (center p at {1, -1, 0})       d (at {2, -1, 0})
     *
     * after rotation:
     *
     *      d (now at {1, -1, -1})
     *
     *      p (centre p at {1,0,0})
     */
    TSM_ASSERT(
        "Rotate detector around origin = root centre. It should reposition!",
        detector2UpdatedPosition.isApprox(Vector3d{1, -1, -1}));
  }

  void test_detector_indexes() {

    auto infos = makeTreeExample();
    const auto &compInfo = std::get<0>(infos);
    /*
    Note that detectors are always the first n component indexes!
    */
    TS_ASSERT_EQUALS(compInfo.detectorsInSubtree(0), std::vector<size_t>{0});
    TS_ASSERT_EQUALS(compInfo.detectorsInSubtree(1), std::vector<size_t>{1});
    TS_ASSERT_EQUALS(compInfo.detectorsInSubtree(2), std::vector<size_t>{2});

    // Now we have non-detector components
    TS_ASSERT_EQUALS(compInfo.detectorsInSubtree(4 /*component index of root*/),
                     std::vector<size_t>({0, 2, 1}));
    TS_ASSERT_EQUALS(
        compInfo.detectorsInSubtree(3 /*component index of sub-assembly*/),
        std::vector<size_t>({0, 2}));
  }

  void test_component_indexes() {

    auto infos = makeTreeExample();
    const auto &compInfo = std::get<0>(infos);
    /*
    Note that detectors are always the first n component indexes!
    */
    TS_ASSERT_EQUALS(compInfo.componentsInSubtree(0), std::vector<size_t>{0});
    TS_ASSERT_EQUALS(compInfo.componentsInSubtree(1), std::vector<size_t>{1});
    TS_ASSERT_EQUALS(compInfo.componentsInSubtree(2), std::vector<size_t>{2});

    // Now we have non-detector components
    TS_ASSERT_EQUALS(
        compInfo.componentsInSubtree(4 /*component index of root*/),
        std::vector<size_t>(
            {0, 2, 3, 1, 4})); // Note inclusion of self comp index

    TS_ASSERT_EQUALS(
        compInfo.componentsInSubtree(3 /*component index of sub-assembly*/),
        std::vector<size_t>({0, 2, 3})); // Note inclusion of self comp index
  }

  void test_parent_component_indices() {
    auto infos = makeTreeExample();
    const auto &compInfo = std::get<0>(infos);
    TSM_ASSERT_EQUALS("Root component's parent index is self", 4,
                      compInfo.parent(4));
    TSM_ASSERT_EQUALS("Parent of detector 0 is assembly index 3", 3,
                      compInfo.parent(0));
  }
};
#endif /* MANTID_BEAMLINE_COMPONENTINFOTEST_H_ */
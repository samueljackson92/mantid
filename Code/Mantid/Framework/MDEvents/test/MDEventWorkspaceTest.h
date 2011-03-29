#ifndef MDEVENTWORKSPACETEST_H
#define MDEVENTWORKSPACETEST_H

#include <cxxtest/TestSuite.h>

#include "MantidAPI/Dimension.h"
#include "MantidKernel/ProgressText.h"
#include "MantidKernel/Timer.h"
#include "MantidMDEvents/BoxController.h"
#include "MantidMDEvents/MDBox.h"
#include "MantidMDEvents/MDEvent.h"
#include "MantidMDEvents/MDEventFactory.h"
#include "MantidMDEvents/MDEventWorkspace.h"
#include "MantidMDEvents/MDGridBox.h"
#include <boost/random/linear_congruential.hpp>
#include <boost/random/mersenne_twister.hpp>
#include <boost/random/uniform_int.hpp>
#include <boost/random/uniform_real.hpp>
#include <boost/random/variate_generator.hpp>
#include <map>
#include <memory>
#include <vector>

using namespace Mantid;
using namespace Mantid::Kernel;
using namespace Mantid::MDEvents;
using namespace Mantid::API;
using namespace Mantid::Geometry;

class MDEventWorkspaceTest :    public CxxTest::TestSuite
{
public:
  bool DODEBUG;
  MDEventWorkspaceTest()
  {
    DODEBUG = false;
  }


  void test_Constructor()
  {
    MDEventWorkspace<MDEvent<3>, 3> ew3;
    TS_ASSERT_EQUALS( ew3.getNumDims(), 3);
    TS_ASSERT_EQUALS( ew3.getNPoints(), 0);
    TS_ASSERT_EQUALS( ew3.id(), "MDEventWorkspace<MDEvent,3>");
  }

  void test_Constructor_IMDEventWorkspace()
  {
    IMDEventWorkspace * ew3 = new MDEventWorkspace<MDEvent<3>, 3>();
    TS_ASSERT_EQUALS( ew3->getNumDims(), 3);
    TS_ASSERT_EQUALS( ew3->getNPoints(), 0);
    delete ew3;
  }

  void test_initialize_throws()
  {
    IMDEventWorkspace * ew = new MDEventWorkspace<MDEvent<3>, 3>();
    TS_ASSERT_THROWS( ew->initialize(), std::runtime_error);
    for (size_t i=0; i<5; i++)
      ew->addDimension( Dimension(-1,1,"x","m") );
    TS_ASSERT_THROWS( ew->initialize(), std::runtime_error);
    delete ew;
  }

  void test_initialize()
  {
    IMDEventWorkspace * ew = new MDEventWorkspace<MDEvent<3>, 3>();
    TS_ASSERT_THROWS( ew->initialize(), std::runtime_error);
    for (size_t i=0; i<3; i++)
      ew->addDimension( Dimension(-1,1,"x","m") );
    TS_ASSERT_THROWS_NOTHING( ew->initialize() );
    delete ew;
  }


  void test_splitBox()
  {
    MDEventWorkspace3 * ew = new MDEventWorkspace3();
    BoxController_sptr bc(new BoxController(3));
    bc->setSplitInto(4);
    ew->setBoxController(bc);
    TS_ASSERT( !ew->isGridBox() );
    TS_ASSERT_THROWS_NOTHING( ew->splitBox(); )
    TS_ASSERT( ew->isGridBox() );
    delete ew;
  }

  /** Adding dimension info and searching for it back */
  void test_addDimension_getDimension()
  {
    MDEventWorkspace2 * ew = new MDEventWorkspace2();
    Dimension dim(-1, +1, "Qx", "Ang");
    TS_ASSERT_THROWS_NOTHING( ew->addDimension(dim); )
    Dimension dim2(-1, +1, "Qy", "Ang");
    TS_ASSERT_THROWS_NOTHING( ew->addDimension(dim2); )
    TS_ASSERT_EQUALS( ew->getNumDims(), 2);
    TS_ASSERT_EQUALS( ew->getDimension(0).getName(), "Qx");
    TS_ASSERT_EQUALS( ew->getDimension(1).getName(), "Qy");
    TS_ASSERT_EQUALS( ew->getDimensionIndexByName("Qx"), 0);
    TS_ASSERT_EQUALS( ew->getDimensionIndexByName("Qy"), 1);
    TS_ASSERT_THROWS_ANYTHING( ew->getDimensionIndexByName("IDontExist"));
  }



  /** Create a test MDEventWorkspace<nd> . Dimensions are names Axis0, Axis1, etc.
   *
   * @param splitInto :: each dimension will split into this many subgrids
   * @return
   */
  template<size_t nd>
  boost::shared_ptr<MDEventWorkspace<MDEvent<nd>,nd> > makeMDEW(size_t splitInto, double min, double max)
  {
    boost::shared_ptr<MDEventWorkspace<MDEvent<nd>,nd> >  out(new MDEventWorkspace<MDEvent<nd>,nd>());
    BoxController_sptr bc(new BoxController(nd));
    bc->setSplitThreshold(5);
    bc->setSplitInto(splitInto);
    out->setBoxController(bc);

    for (size_t d=0; d<nd;d++)
    {
      std::ostringstream name;
      name << "Axis" << d;
      Dimension dim(min, max, name.str(), "m");
      out->addDimension(dim);
    }
    out->initialize();
    return out;
  }



  //-------------------------------------------------------------------------------------
  /** Fill a 10x10 gridbox with events
   *
   * Tests that bad events are thrown out when using addEvents.
   * */
  void test_addManyEvents()
  {
    ProgressText * prog = NULL;
    if (DODEBUG) prog = new ProgressText(0.0, 1.0, 10, false);

    typedef MDGridBox<MDEvent<2>,2> box_t;
    MDEventWorkspace2::sptr b = makeMDEW<2>(10, 0.0, 10.0);
    box_t * subbox;

    // Manually set some of the tasking parameters
    b->getBoxController()->m_addingEvents_eventsPerTask = 1000;
    b->getBoxController()->m_addingEvents_numTasksPerBlock = 20;
    b->getBoxController()->m_SplitThreshold = 100;
    b->getBoxController()->m_maxDepth = 4;

    std::vector< MDEvent<2> > events;
    size_t num_repeat = 1000;
    // Make an event in the middle of each box
    for (double x=0.0005; x < 10; x += 1.0)
      for (double y=0.0005; y < 10; y += 1.0)
      {
        for (size_t i=0; i < num_repeat; i++)
        {
          double centers[2] = {x, y};
          events.push_back( MDEvent<2>(2.0, 2.0, centers) );
        }
      }
    TS_ASSERT_EQUALS( events.size(), 100*num_repeat);

    TS_ASSERT_THROWS_NOTHING( b->addManyEvents( events, prog ); );
    TS_ASSERT_EQUALS( b->getNPoints(), 100*num_repeat);
    TS_ASSERT_EQUALS( b->getBox()->getSignal(), 100*num_repeat*2.0);
    TS_ASSERT_EQUALS( b->getBox()->getErrorSquared(), 100*num_repeat*2.0);

    box_t * gridBox = dynamic_cast<box_t *>(b->getBox());
    std::vector<IMDBox<MDEvent<2>,2>*> boxes = gridBox->getBoxes();
    TS_ASSERT_EQUALS( boxes[0]->getNPoints(), num_repeat);
    // The box should have been split itself into a gridbox, because 1000 events > the split threshold.
    subbox = dynamic_cast<box_t *>(boxes[0]);
    TS_ASSERT( subbox ); if (!subbox) return;
    // The sub box is at a depth of 1.
    TS_ASSERT_EQUALS( subbox->getDepth(), 1);

    // And you can keep recursing into the box.
    boxes = subbox->getBoxes();
    subbox = dynamic_cast<box_t *>(boxes[0]);
    TS_ASSERT( subbox ); if (!subbox) return;
    TS_ASSERT_EQUALS( subbox->getDepth(), 2);

    // And so on (this type of recursion was checked in test_splitAllIfNeeded()
    if (prog) delete prog;
  }


//
//  //-------------------------------------------------------------------------------------
//  /** Tests that bad events are thrown out when using addEvents.
//   * */
//  void test_addManyEvents_Performance()
//  {
//    // This test is too slow for unit tests, so it is disabled except in debug mode.
//    if (!DODEBUG) return;
//
//    ProgressText * prog = new ProgressText(0.0, 1.0, 10, true);
//    prog->setNotifyStep(0.5); //Notify more often
//
//    typedef MDGridBox<MDEvent<2>,2> box_t;
//    box_t * b = makeMDEW<2>(10, 0.0, 10.0);
//
//    // Manually set some of the tasking parameters
//    b->getBoxController()->m_addingEvents_eventsPerTask = 50000;
//    b->getBoxController()->m_addingEvents_numTasksPerBlock = 50;
//    b->getBoxController()->m_SplitThreshold = 1000;
//    b->getBoxController()->m_maxDepth = 6;
//
//    Timer tim;
//    std::vector< MDEvent<2> > events;
//    double step_size = 1e-3;
//    size_t numPoints = (10.0/step_size)*(10.0/step_size);
//    std::cout << "Starting to write out " << numPoints << " events\n";
//    if (true)
//    {
//      // ------ Make an event in the middle of each box ------
//      for (double x=step_size; x < 10; x += step_size)
//        for (double y=step_size; y < 10; y += step_size)
//        {
//          double centers[2] = {x, y};
//          events.push_back( MDEvent<2>(2.0, 3.0, centers) );
//        }
//    }
//    else
//    {
//      // ------- Randomize event distribution ----------
//      boost::mt19937 rng;
//      boost::uniform_real<float> u(0.0, 10.0); // Range
//      boost::variate_generator<boost::mt19937&, boost::uniform_real<float> > gen(rng, u);
//
//      for (size_t i=0; i < numPoints; i++)
//      {
//        double centers[2] = {gen(), gen()};
//        events.push_back( MDEvent<2>(2.0, 3.0, centers) );
//      }
//    }
//    TS_ASSERT_EQUALS( events.size(), numPoints);
//    std::cout << "..." << numPoints << " events were filled in " << tim.elapsed() << " secs.\n";
//
//    size_t numbad = 0;
//    TS_ASSERT_THROWS_NOTHING( numbad = b->addManyEvents( events, prog); );
//    TS_ASSERT_EQUALS( numbad, 0);
//    TS_ASSERT_EQUALS( b->getNPoints(), numPoints);
//    TS_ASSERT_EQUALS( b->getSignal(), numPoints*2.0);
//    TS_ASSERT_EQUALS( b->getErrorSquared(), numPoints*3.0);
//
//    std::cout << "addManyEvents() ran in " << tim.elapsed() << " secs.\n";
//  }



  /** Test binning into up to 4 dense histogram dimensions. */
  void do_test_centerpointBinToMDHistoWorkspace( std::string name1, std::string name2, std::string name3, std::string name4,
      size_t expected_events_per_bin)
  {
    size_t len = 10; // Make the box split into 12x12x12
    double size = len * 1.0;  // Make each grid box 1.0 in size
    size_t binlen = 5; // And bin more coarsely, 4x4x4

    // 10x10x10 eventWorkspace
    MDEventWorkspace3::sptr ws = makeMDEW<3>(len, 0.0, size);

    // Put one event per bin
    for (size_t x=0; x<len; x++)
      for (size_t y=0; y<len; y++)
        for (size_t z=0; z<len; z++)
        {
          CoordType centers[3] = {x+0.5,y+0.5,z+0.5};
          ws->addEvent( MDEvent<3>(1.0, 2.0, centers) );
        }

    // Split the box, serially.
    ws->splitBox();
    ws->splitAllIfNeeded(NULL);
    ws->refreshCache();
    TS_ASSERT_EQUALS( ws->getNPoints(), len*len*len);
    TS_ASSERT_DELTA( ws->getBox()->getSignal(), len*len*len, 1e-5);

    // Will bin it into a 5x5x5 workspace
    std::vector<MDHistoDimension_sptr> dims;
    dims.push_back(MDHistoDimension_sptr(new MDHistoDimension(name1, "id0", 0, size, name1 != "NONE" ? binlen : 1)));
    dims.push_back(MDHistoDimension_sptr(new MDHistoDimension(name2, "id1", 0, size, name2 != "NONE" ? binlen : 1)));
    dims.push_back(MDHistoDimension_sptr(new MDHistoDimension(name3, "id2", 0, size, name3 != "NONE" ? binlen : 1)));
    dims.push_back(MDHistoDimension_sptr(new MDHistoDimension(name4, "id3", 0, size, name4 != "NONE" ? binlen : 1)));

    // Call the method
    MDHistoWorkspace_sptr out;
    ProgressText * prog = new ProgressText(0, 1.0, 1); // The function will set the # of steps
    prog = NULL;
    TS_ASSERT_THROWS_NOTHING( out = ws->centerpointBinToMDHistoWorkspace(dims[0], dims[1], dims[2], dims[3], prog) );
    TS_ASSERT(out);


    // How many points should be in the output?
    size_t numPointsExpected = 1;
    for (size_t i=0; i<4; i++)
      numPointsExpected *= dims[i]->getNBins();
    TS_ASSERT_EQUALS(out->getNPoints(), numPointsExpected);

    for (size_t i=0; i < out->getNPoints(); i++)
    {
      TS_ASSERT_DELTA( out->getSignalAt(i), expected_events_per_bin * 1.0, 1e-5 );
      TS_ASSERT_DELTA( out->getErrorAt(i), expected_events_per_bin * 2.0, 1e-5 );
    }

  }


  void test_centerpointBinToMDHistoWorkspace_3D()
  {
    do_test_centerpointBinToMDHistoWorkspace("Axis0", "Axis1", "Axis2", "NONE", 8);
  }

  void test_centerpointBinToMDHistoWorkspace_3D_scrambled_order()
  {
    do_test_centerpointBinToMDHistoWorkspace("Axis1", "Axis0", "NONE", "Axis2", 8); // 2x2x2 blocks
  }

  void test_centerpointBinToMDHistoWorkspace_2D()
  {
    do_test_centerpointBinToMDHistoWorkspace("Axis0", "Axis1", "NONE", "NONE", 40); // 2x2x10 blocks
  }

  void test_centerpointBinToMDHistoWorkspace_1D()
  {
    do_test_centerpointBinToMDHistoWorkspace("NONE", "Axis2", "NONE", "NONE", 200); // 2x10x10 blocks
  }


};

#endif

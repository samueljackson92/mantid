/*WIKI* 



For testing MDEventWorkspaces, this algorithm either creates a uniform, random distribution of events, 
or generate regular events placed in boxes, or fills peaks around given points with a given number of events.





*WIKI*/
#include "MantidKernel/ArrayProperty.h"
#include "MantidKernel/System.h"
#include "MantidMDAlgorithms/FakeMDEventData.h"
#include "MantidMDEvents/MDEventFactory.h"
#include "MantidMDEvents/MDEventWorkspace.h"
#include <boost/math/distributions/normal.hpp>
#include <boost/math/special_functions/fpclassify.hpp>
#include <boost/math/special_functions/pow.hpp>
#include <boost/random/linear_congruential.hpp>
#include <boost/random/mersenne_twister.hpp>
#include <boost/random/uniform_int.hpp>
#include <boost/random/uniform_real.hpp>
#include <boost/random/variate_generator.hpp>
#include <math.h>
#include "MantidKernel/ThreadScheduler.h"
#include "MantidKernel/ThreadPool.h"
#include "MantidKernel/VectorHelper.h"
#include "MantidKernel/Utils.h"
#include <cfloat>

namespace Mantid
{
namespace MDAlgorithms
{

  // Register the algorithm into the AlgorithmFactory
  DECLARE_ALGORITHM(FakeMDEventData)
  
  using namespace Mantid::Kernel;
  using namespace Mantid::API;
  using namespace Mantid::MDEvents;


  //----------------------------------------------------------------------------------------------
  /** Constructor
   */
  FakeMDEventData::FakeMDEventData()
  {
  }
    
  //----------------------------------------------------------------------------------------------
  /** Destructor
   */
  FakeMDEventData::~FakeMDEventData()
  {
  }

  //----------------------------------------------------------------------------------------------
  /// Sets documentation strings for this algorithm
  void FakeMDEventData::initDocs()
  {
    this->setWikiSummary("Adds fake multi-dimensional event data to an existing MDEventWorkspace, for use in testing.\nYou can create a blank MDEventWorkspace with CreateMDWorkspace.");
    this->setOptionalMessage("Adds fake multi-dimensional event data to an existing MDEventWorkspace, for use in testing.\nYou can create a blank MDEventWorkspace with CreateMDWorkspace.");
  }

  //----------------------------------------------------------------------------------------------
  /** Initialize the algorithm's properties.
   */
  void FakeMDEventData::init()
  {
    declareProperty(new WorkspaceProperty<IMDEventWorkspace>("InputWorkspace","",Direction::InOut),
        "An input workspace, that will get MDEvents added to it");

    declareProperty(new ArrayProperty<double>("UniformParams", ""),
        "Add a uniform, randomized distribution of events.\n"
        "1 parameter: number_of_events; they will be distributed across the size of the workspace.\n"
        "Depending on the sighn of this parameter, the events are either distributed randomly around the box \n"
        "(Case 1, positive) or placed on the regular grid through the box (Case 2, negative)\n"
        "Treatmetn of Multiple parameters: depends on the Case\n"
        "Case 1: number_of_events, min,max (for each dimension); distribute the events inside the range given.\n"
        "Case 2: Additional parameters describe initial location and steps of the regular grid in each dimension\n");

    declareProperty(new ArrayProperty<double>("PeakParams", ""),
        "Add a peak with a normal distribution around a central point.\n"
        "Parameters: number_of_events, x, y, z, ..., radius.\n");

    declareProperty(new PropertyWithValue<int>("RandomSeed", 0),
        "Seed int for the random number generator.");

    declareProperty(new PropertyWithValue<bool>("RandomizeSignal", false),
        "If true, the events' signal and error values will be randomized around 1.0+-0.5.");

  }



  //----------------------------------------------------------------------------------------------
  /** Function makes up a fake single-crystal peak and adds it to the workspace.
   *
   * @param ws
   */
  template<typename MDE, size_t nd>
  void FakeMDEventData::addFakePeak(typename MDEventWorkspace<MDE, nd>::sptr ws)
  {
    std::vector<double> params = getProperty("PeakParams");
    bool RandomizeSignal = getProperty("RandomizeSignal");
    if (params.size() == 0)
      return;

    if (params.size() != nd + 2)
      throw std::invalid_argument("PeakParams needs to have ndims+2 arguments.");
    if (params[0] <= 0)
      throw std::invalid_argument("PeakParams: number_of_events needs to be > 0");
    size_t num = size_t(params[0]);

    Progress prog(this, 0.0, 1.0, 100);
    size_t progIncrement = num / 100; if (progIncrement == 0) progIncrement = 1;

    // Width of the peak
    double desiredRadius = params.back();

    boost::mt19937 rng;
    boost::uniform_real<coord_t> u2(0, 1.0); // Random from 0 to 1.0
    boost::variate_generator<boost::mt19937&, boost::uniform_real<coord_t> > genUnit(rng, u2);
    int randomSeed = getProperty("RandomSeed");
    rng.seed((unsigned int)(randomSeed));

    for (size_t i=0; i<num; ++i)
    {
      // Algorithm to generate points along a random n-sphere (sphere with not necessarily 3 dimensions)
      // from http://en.wikipedia.org/wiki/N-sphere as of May 6, 2011.

      // First, points in a hyper-cube of size 1.0, centered at 0.
      coord_t centers[nd];
      coord_t radiusSquared = 0;
      for (size_t d=0; d<nd; d++)
      {
        centers[d] = genUnit()-0.5f; // Distribute around +- the center
        radiusSquared += centers[d]*centers[d];
      }

      // Make a unit vector pointing in this direction
      coord_t radius = static_cast<coord_t>(sqrt(radiusSquared));
      for (size_t d=0; d<nd; d++)
        centers[d] /= radius;

      // Now place the point along this radius, scaled with ^1/n for uniformity.
      coord_t radPos = genUnit();
      radPos = static_cast<coord_t>(pow(radPos, static_cast<coord_t>(1.0/static_cast<coord_t>(nd))));
      for (size_t d=0; d<nd; d++)
      {
        // Multiply by the scaling and the desired peak radius
        centers[d] *= (radPos * static_cast<coord_t>(desiredRadius));
        // Also offset by the center of the peak, as taken in Params
        centers[d] += static_cast<coord_t>(params[d+1]);
      }

      // Default or randomized error/signal
      float signal = 1.0;
      float errorSquared = 1.0;
      if (RandomizeSignal)
      {
        signal = float(0.5 + genUnit());
        errorSquared = float(0.5 + genUnit());
      }

      // Create and add the event.
      ws->addEvent( MDE( signal, errorSquared, centers) );
      // Progress report
      if ((i % progIncrement) == 0) prog.report();
    }

    ws->splitBox();
    Kernel::ThreadScheduler * ts = new ThreadSchedulerFIFO();
    ThreadPool tp(ts);
    ws->splitAllIfNeeded(ts);
    tp.joinAll();
    ws->refreshCache();
  }

  //----------------------------------------------------------------------------------------------
  /** Function makes up a fake uniform event data and adds it to the workspace.
   *
   * @param ws
   */
  template<typename MDE, size_t nd>
  void FakeMDEventData::addFakeUniformData(typename MDEventWorkspace<MDE, nd>::sptr ws)
  {
    std::vector<double> params = getProperty("UniformParams");
    if (params.size() == 0)
      return;

    bool randomEvents=true;
    if (params[0] < 0)
    {
      randomEvents=false;
      params[0] = -params[0];
    }

    if (params.size() == 1)
    {
      if(randomEvents)
      {
        for (size_t d=0; d<nd; ++d)
        {
            params.push_back( ws->getDimension(d)->getMinimum() );
            params.push_back( ws->getDimension(d)->getMaximum() );
        }
      }
      else   // regular events
      {
        for (size_t d=0; d<nd; ++d)
        {
            params.push_back( ws->getDimension(d)->getMinimum() );
            size_t nStrides = ws->getDimension(d)->getNBins();
            if(nStrides<1 || nStrides>=size_t(-1))nStrides = 1;            
            params.push_back((ws->getDimension(d)->getMaximum()-ws->getDimension(d)->getMinimum())/nStrides);
        }
      }
    }
    if ((params.size() != 1 + nd*2))
      throw std::invalid_argument("UniformParams: needs to have ndims*2+1 arguments ");


    if(randomEvents)
      addFakeRandomData<MDE,nd>(params,ws);
    else      
      addFakeRegularData<MDE,nd>(params,ws);
  

    ws->splitBox();
    Kernel::ThreadScheduler * ts = new ThreadSchedulerFIFO();
    ThreadPool tp(ts);
    ws->splitAllIfNeeded(ts);
    tp.joinAll();
    ws->refreshCache();

  }

  template<typename MDE, size_t nd>
  void FakeMDEventData::addFakeRandomData(const std::vector<double> &params,typename MDEventWorkspace<MDE, nd>::sptr ws)
  {

    bool RandomizeSignal = getProperty("RandomizeSignal");

    size_t num = size_t(params[0]);
    if(num==0) throw std::invalid_argument(" number of distributed events can not be equal to 0");


    Progress prog(this, 0.0, 1.0, 100);
    size_t progIncrement = num / 100; if (progIncrement == 0) progIncrement = 1;


    boost::mt19937 rng;
    int randomSeed = getProperty("RandomSeed");
    rng.seed((unsigned int)(randomSeed));
 
    // Unit-size randomizer
    boost::uniform_real<double> u2(0, 1.0); // Random from 0 to 1.0
    boost::variate_generator<boost::mt19937&, boost::uniform_real<double> > genUnit(rng, u2);

    // Make a random generator for each dimensions
    typedef boost::variate_generator<boost::mt19937&, boost::uniform_real<double> >   gen_t;

    gen_t * gens[nd];
    for (size_t d=0; d<nd; ++d)
    {
      double min = params[d*2+1];
      double max = params[d*2+2];
      if (max <= min) throw std::invalid_argument("UniformParams: min must be < max for all dimensions.");

      boost::uniform_real<double> u(min,max); // Range
      gen_t * gen = new gen_t(rng, u);
      gens[d] = gen;
    }
 

    // Create all the requested events
    for (size_t i=0; i<num; ++i)
    {
      coord_t centers[nd];
      for (size_t d=0; d<nd; d++)
      {
          centers[d] = static_cast<coord_t>((*gens[d])()); // use a different generator for each dimension
      }


      // Default or randomized error/signal
      float signal = 1.0;
      float errorSquared = 1.0;
      if (RandomizeSignal)
      {
        signal = float(0.5 + genUnit());
        errorSquared = float(0.5 + genUnit());
      }

      // Create and add the event.
      ws->addEvent( MDE( signal, errorSquared, centers) );
      // Progress report
      if ((i % progIncrement) == 0) prog.report();
    }

    /// Clean up the generators
    for (size_t d=0; d<nd; ++d)
      delete gens[d];

  }

  template<typename MDE, size_t nd>
  void FakeMDEventData::addFakeRegularData(const std::vector<double> &params,typename MDEventWorkspace<MDE, nd>::sptr ws)
  {
    // the parameters for regular distribution of events over the box
    std::vector<double> minPar(nd),delta(nd);
    std::vector<size_t> nStrides(nd);
    size_t gridSize(0);

    //bool RandomizeSignal = getProperty("RandomizeSignal");

    size_t num = size_t(params[0]);
    if(num==0)
      throw std::invalid_argument(" number of distributed events can not be equal to 0");


    Progress prog(this, 0.0, 1.0, 100);
    size_t progIncrement = num / 100; if (progIncrement == 0) progIncrement = 1;

    gridSize=1;
    for (size_t d=0; d<nd; ++d)
    {
      double min  = ws->getDimension(d)->getMinimum(); 
      double max  = ws->getDimension(d)->getMaximum();
      minPar[d]   = params[d*2+1];
      double step = params[d*2+2];
      if ((minPar[d] < min)||(minPar[d] >= max)) throw std::invalid_argument("RegularData: starting point must be within the box for all dimensions.");
      if ((minPar[d]<0) ||(minPar[d]>step))throw  std::invalid_argument("RegularData: initial point must be within the sep and be positive for all dimensions.");
      if(minPar[d]==step)minPar[d]=step*(1-FLT_EPSILON);

      delta[d]  = step;
      if(step<=0)
        throw(std::invalid_argument("Step of the regular grid is less or equal to 0"));

      nStrides[d] = size_t((max-min)/step);
      if(nStrides[d]<1)
      {
        minPar[d]=min;
        delta[d] = (max-min);
        nStrides[d]=1;
      }

      gridSize*=(nStrides[d]+1);

    }
    // Create all the requested events
    std::vector<size_t> indexes;
    size_t cellCount(0);
    for (size_t i=0; i<num; ++i)
    {
      coord_t centers[nd];

      Kernel::Utils::getIndicesFromLinearIndex(cellCount,nStrides,indexes);
      ++cellCount;
      if(cellCount>=gridSize)cellCount=0;

      for (size_t d=0; d<nd; d++)
      {
         centers[d]= coord_t(minPar[d]+delta[d]*double(indexes[d]));
      }

      // Default or randomized error/signal
      float signal = 1.0;
      float errorSquared = 1.0;
      //if (RandomizeSignal)
      //{
      //  signal = float(0.5 + genUnit());
      //  errorSquared = float(0.5 + genUnit());
      //}

      // Create and add the event.
      ws->addEvent( MDE( signal, errorSquared, centers) );
      // Progress report
      if ((i % progIncrement) == 0) prog.report();
    }

  }


  //----------------------------------------------------------------------------------------------
  /** Execute the algorithm.
   */
  void FakeMDEventData::exec()
  {
    IMDEventWorkspace_sptr in_ws = getProperty("InputWorkspace");

    if (getPropertyValue("UniformParams")=="" && getPropertyValue("PeakParams")=="")
      throw std::invalid_argument("You must specify at least one of PeakParams or UniformParams.");

    CALL_MDEVENT_FUNCTION(this->addFakePeak, in_ws)
    CALL_MDEVENT_FUNCTION(this->addFakeUniformData, in_ws)

    // Mark that events were added, so the file back end (if any) needs updating
    in_ws->setFileNeedsUpdating(true);
  }



} // namespace Mantid
} // namespace MDEvents


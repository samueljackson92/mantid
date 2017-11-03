#include "MantidKernel/PropertyWithValue.h"
#include "MantidAPI/DllConfig.h"
//#include "MantidCrystal/UnitCellProperty.h"
#include "MantidGeometry/Crystal/UnitCell.h"

// PropertyWithValue implementation
#include "MantidKernel/PropertyWithValue.tcc"
using namespace Mantid;

namespace Mantid {
namespace Kernel {

template class  
    PropertyWithValue<boost::shared_ptr<Geometry::UnitCell>>;

}
}


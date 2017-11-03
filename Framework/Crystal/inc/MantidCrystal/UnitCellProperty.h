#ifndef MANTID_CRYSTAL_UNITCELLPROPERTY_H_
#define MANTID_CRYSTAL_UNITCELLPROPERTY_H_

//-----------------------------------------------------------------
// Includes
//-----------------------------------------------------------------
#include "MantidAPI/DllConfig.h"
#include "MantidKernel/PropertyWithValue.h"
#include "MantidGeometry/Crystal/UnitCell.h"
#include <boost/shared_ptr.hpp>


namespace Mantid {
namespace Crystal {


class DLLExport UnitCellProperty : public Kernel::PropertyWithValue<boost::shared_ptr<Geometry::UnitCell>> {
public:
  explicit UnitCellProperty(const std::string &name)
    : Kernel::PropertyWithValue<boost::shared_ptr<Geometry::UnitCell>>(
          name, boost::shared_ptr<Geometry::UnitCell>()) {};
  /// 'Virtual copy constructor
  boost::shared_ptr<Geometry::UnitCell> &
  operator=(const boost::shared_ptr<Geometry::UnitCell> &value) override { 
      return Kernel::PropertyWithValue<boost::shared_ptr<Geometry::UnitCell>>::operator=(value);
  };

  UnitCellProperty &operator+=(Kernel::Property const *) override {
      throw Kernel::Exception::NotImplementedError(
              "+= operator is not implemented for WorkspaceProperty.");
      return *this;
  };

  UnitCellProperty *clone() const override { return new UnitCellProperty(*this); };

  std::string value() const override { return ""; };

  bool isValueSerializable() const override { return false; };

  std::string getDefault() const override { return ""; };

  std::string setValue(const std::string &value) override { return ""; };

  std::string
  setDataItem(const boost::shared_ptr<Kernel::DataItem> value) override;

  std::string isValid() const override { return ""; };

  bool isDefault() const override { return false; };

  const Kernel::PropertyHistory createHistory() const override;
};
}
}



#endif 

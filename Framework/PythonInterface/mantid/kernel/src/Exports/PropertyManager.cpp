#ifdef _MSC_VER
#pragma warning(disable : 4250) // Disable warning regarding inheritance via
                                // dominance, we have no way around it with the
                                // design
#endif
#include "MantidPythonInterface/kernel/GetPointer.h"
#include "MantidKernel/IPropertyManager.h"
#include "MantidKernel/PropertyManager.h"

#include <string>
#include <boost/python/class.hpp>
#include <boost/python/overloads.hpp>

using Mantid::Kernel::IPropertyManager;
using Mantid::Kernel::PropertyManager;

using namespace boost::python;

GET_POINTER_SPECIALIZATION(PropertyManager);

namespace {
#ifdef __clang__
#pragma clang diagnostic push
#pragma clang diagnostic ignored "-Wunknown-pragmas"
#pragma clang diagnostic ignored "-Wunused-local-typedef"
#endif
  BOOST_PYTHON_MEMBER_FUNCTION_OVERLOADS(asStringOverloader, asString, 0, 1)
    BOOST_PYTHON_MEMBER_FUNCTION_OVERLOADS(getPropertiesOverloader, setProperties, 1, 2)
#ifdef __clang__
#pragma clang diagnostic pop
#endif

}

void (PropertyManager::*setPropertiesWrapper)(const std::string &, const std::unordered_set<std::string>&) = &PropertyManager::setProperties;

void export_PropertyManager() {
  typedef boost::shared_ptr<PropertyManager> PropertyManager_sptr;

  // The second argument defines the actual type held within the Python object.
  // This means that when a PropertyManager is constructed in Python it actually
  // used
  // a shared_ptr to the object rather than a raw pointer. This knowledge is
  // used by
  // DataServiceExporter::extractCppValue to assume that it can always extract a
  // shared_ptr
  // type
  class_<PropertyManager, PropertyManager_sptr, bases<IPropertyManager>,
         boost::noncopyable>("PropertyManager")
    .def("asString", (&PropertyManager::asString), 
      asStringOverloader((arg("self"), arg("withDefaultValues")=false),
      "Return the property manager serialized as a string."))
    .def("setProperties", setPropertiesWrapper,
      getPropertiesOverloader((arg("self"), arg("propertiesJson"), arg("ignoreProperties")),
      "Sets all the declared properties from Json-like string."));


  //void setProperties(const std::string &propertiesJson,
  //  const std::unordered_set<std::string> &ignoreProperties =
  //  std::unordered_set<std::string>()) override;
}

#ifdef _MSC_VER
#pragma warning(default : 4250)
#endif

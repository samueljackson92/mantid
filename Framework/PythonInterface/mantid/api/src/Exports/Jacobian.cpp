#include "MantidAPI/Jacobian.h"
#include "MantidPythonInterface/kernel/GetPointer.h"
#include <boost/python/class.hpp>
#include <boost/python/register_ptr_to_python.hpp>

using Mantid::API::Jacobian;
using namespace boost::python;

GET_POINTER_SPECIALIZATION(Jacobian)

void export_Jacobian() {
  register_ptr_to_python<Jacobian *>();

  class_<Jacobian, boost::noncopyable>("Jacobian", no_init)
      .def("set", &Jacobian::set,
           (arg("self"), arg("iy"), arg("ip"), arg("value")),
           "Set an element of the Jacobian matrix where iy=index of data "
           "point, ip=index of parameter.")

      .def("get", &Jacobian::get, (arg("self"), arg("iy"), arg("ip")),
           "Return the given element of the Jacobian matrix where iy=index of "
           "data point, ip=index of parameter.");
}

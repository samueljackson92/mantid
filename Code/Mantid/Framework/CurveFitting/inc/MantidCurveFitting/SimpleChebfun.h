#ifndef MANTID_CURVEFITTING_SIMPLECHEBFUN_H_
#define MANTID_CURVEFITTING_SIMPLECHEBFUN_H_

#include "MantidKernel/System.h"
#include "MantidCurveFitting/ChebfunBase.h"

namespace Mantid {
namespace CurveFitting {

/** SimpleChebfun : approximates smooth 1d functions and
  provides methods to manipulate them.

  Main functionality is implemented in ChebfunBase class.

  Copyright &copy; 2015 ISIS Rutherford Appleton Laboratory, NScD Oak Ridge
  National Laboratory & European Spallation Source

  This file is part of Mantid.

  Mantid is free software; you can redistribute it and/or modify
  it under the terms of the GNU General Public License as published by
  the Free Software Foundation; either version 3 of the License, or
  (at your option) any later version.

  Mantid is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  GNU General Public License for more details.

  You should have received a copy of the GNU General Public License
  along with this program.  If not, see <http://www.gnu.org/licenses/>.

  File change history is stored at: <https://github.com/mantidproject/mantid>
  Code Documentation is available at: <http://doxygen.mantidproject.org>
*/
class DLLExport SimpleChebfun {
public:
  /// Constructor.
  SimpleChebfun(size_t n, ChebfunFunctionType fun, double start, double end);
  /// Constructor.
  SimpleChebfun(ChebfunFunctionType fun, double start, double end, double accuracy = 0.0, size_t badSize = 10);
  /// Constructor.
  SimpleChebfun(const std::vector<double>& x, const std::vector<double>& y);
  /// Number of points in the approximation.
  size_t size() const {return m_base->size();}
  /// Order of the approximating polynomial.
  size_t order() const {return m_base->order();}
  /// Check if approximation is good.
  bool isGood() const {return !m_badFit;}
  /// Start of the interval
  double startX() const { return m_base->startX(); }
  /// End of the interval
  double endX() const { return m_base->endX(); }
  /// Get the width of the interval
  double width() const { return m_base->width(); }
  /// Get a reference to the x-points
  const std::vector<double> &xPoints() const { return m_base->xPoints(); }
  /// Get a reference to the y-points
  const std::vector<double> &yPoints() const { return m_P; }
  /// Evaluate the function.
  double operator()(double x) const;
  /// Evaluate the function.
  std::vector<double> operator()(const std::vector<double>& x) const;
  /// Create a vector of x values linearly spaced on the approximation interval
  std::vector<double> linspace(size_t n) const;
  /// Create a derivative of this function.
  SimpleChebfun derivative() const;
private:
  /// Constructor
  SimpleChebfun(ChebfunBase_sptr base);
  /// Underlying base that does actual job.
  ChebfunBase_sptr m_base;
  /// Function values at the chebfun x-points.
  std::vector<double> m_P;
  /// Chebyshev expansion coefficients.
  mutable std::vector<double> m_A;

  /// Set in a case of a bad fit
  bool m_badFit;
};

} // namespace CurveFitting
} // namespace Mantid

#endif /* MANTID_CURVEFITTING_SIMPLECHEBFUN_H_ */
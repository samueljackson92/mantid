#include "MantidCurveFitting/SimpleChebfun.h"

#include <boost/make_shared.hpp>

namespace Mantid {
namespace CurveFitting {

//----------------------------------------------------------------------------------------------
/// Constructs a SimpleChebfun that approximates a function with a polynomial of a given order
/// in an interval of x-values.
/// @param n :: Polynomial order == number of points - 1.
/// @param fun :: A function to approximate.
/// @param start :: The start (lower bound) of an interval on the x-axis.
/// @param end :: The end (upper bound) of an interval on the x-axis.
SimpleChebfun::SimpleChebfun(size_t n, ChebfunFunctionType fun, double start,
                             double end)
    : m_badFit(false) {
  m_base = boost::make_shared<ChebfunBase>(n, start, end);
  m_P = m_base->fit(fun);
}

/// Constructs a SimpleChebfun that approximates a function to a given accuracy
/// in an interval of x-values.
/// The approximation may fail (too large interval, function discontinuous, etc).
/// In this case a default sized polynomial is created and isGood() will be
/// returning false.
/// @param fun :: A function to approximate.
/// @param start :: The start (lower bound) of an interval on the x-axis.
/// @param end :: The end (upper bound) of an interval on the x-axis.
/// @param accuracy :: The accuracy of the approximation.
/// @param badSize :: If automatic approxiamtion fails the base will have this size.
SimpleChebfun::SimpleChebfun(ChebfunFunctionType fun, double start, double end,
                             double accuracy, size_t badSize)
    : m_badFit(false) {
  m_base = ChebfunBase::bestFitAnyTolerance<ChebfunFunctionType>(
      start, end, fun, m_P, m_A, accuracy);
  if (!m_base) {
    m_base = boost::make_shared<ChebfunBase>(badSize - 1, start, end, accuracy);
    m_P = m_base->fit(fun);
    m_badFit = true;
  }
}

/// Construct a SimpleChebfun by smoothing data in vectors with x and y data.
/// @param x :: A vector of x values.
/// @param y :: A vector of y values. Must have same size as x.
SimpleChebfun::SimpleChebfun(const std::vector<double> &x,
                             const std::vector<double> &y)
    : m_badFit(false) {
  m_base = boost::make_shared<ChebfunBase>(x.size() - 1, x.front(), x.back());
  m_P = m_base->smooth(x, y);
}

/// Construct an empty SimpleChebfun with shared base.
SimpleChebfun::SimpleChebfun(ChebfunBase_sptr base): m_badFit(false) {
  assert(base);
  m_base = base;
  m_P.resize(base->size());
}

/// Evaluate the function.
/// @param x :: Point where the function is evaluated.
double SimpleChebfun::operator()(double x) const {
  return m_base->eval(x, m_P);
}

/// Evaluate the function for each value in a vector.
/// @param x :: Points where the function is evaluated.
std::vector<double> SimpleChebfun::operator()(const std::vector<double>& x) const {
  return m_base->evalVector(x, m_P);
}

/// Create a vector of x values linearly spaced on the approximation interval.
/// @param n :: Number of points in the vector.
std::vector<double> SimpleChebfun::linspace(size_t n) const {
  return m_base->linspace(n);
}

/// Create a derivative of this function.
SimpleChebfun SimpleChebfun::derivative() const {
  SimpleChebfun cheb(m_base);
  if (m_A.empty()) {
    m_A = m_base->calcA(m_P);
  }
   m_base->derivative(m_A, cheb.m_A);
   cheb.m_P = m_base->calcP(cheb.m_A);
   return cheb;
}


} // namespace CurveFitting
} // namespace Mantid
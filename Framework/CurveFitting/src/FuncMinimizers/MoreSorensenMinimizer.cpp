// This code was originally translated from Fortran code on
// https://ccpforge.cse.rl.ac.uk/gf/project/ral_nlls June 2016
//----------------------------------------------------------------------
// Includes
//----------------------------------------------------------------------
#include "MantidCurveFitting/FuncMinimizers/MoreSorensenMinimizer.h"
#include "MantidAPI/FuncMinimizerFactory.h"
#include "MantidCurveFitting/RalNlls/TrustRegion.h"
#include <cmath>

namespace Mantid {
namespace CurveFitting {
namespace FuncMinimisers {

// clang-format off
///@cond nodoc
DECLARE_FUNCMINIMIZER(MoreSorensenMinimizer,More-Sorensen)
///@endcond
// clang-format on

MoreSorensenMinimizer::MoreSorensenMinimizer() : TrustRegionMinimizer() {}

/// Name of the minimizer.
std::string MoreSorensenMinimizer::name() const { return "More-Sorensen"; }

namespace {

/** Solve a system of linear equations. The system's matrix must be
 *  positive-definite.
 *  @param A :: A matrix of a system of equations.
 *     Must be positive-definite for success.
 *  @param b :: A vector of the right-hand side.
 *  @param LtL :: A work matrix.
 *  @param x :: A vector that receives the solution.
 *  @return true if successful
 */
bool solveSpd(const DoubleFortranMatrix &A, const DoubleFortranVector &b,
              DoubleFortranMatrix &LtL, DoubleFortranVector &x) {
  // Fortran code uses this:
  // dposv('L', n, 1, LtL, n, x, n, inform.external_return)
  // This is the GSL replacement:
  LtL = A;
  auto res = gsl_linalg_cholesky_decomp(LtL.gsl());
  if (res == GSL_EDOM) {
    // Matrix is not positive definite, return for retry.
    return false;
  }
  gsl_linalg_cholesky_solve(LtL.gsl(), b.gsl(), x.gsl());
  return true;
}

/** Calculate the leftmost eigenvalue of a matrix.
 *  @param A :: A matrix to analyse.
 *  @param sigma :: A variable to receive the value of the smallest
 *        eigenvalue.
 *  @param y :: A vector that receives the corresponding eigenvector.
 */
void minEigSymm(const DoubleFortranMatrix &A, double &sigma,
                DoubleFortranVector &y) {
  auto M = A;
  DoubleFortranVector ew;
  DoubleFortranMatrix ev;
  M.eigenSystem(ew, ev);
  auto ind = ew.sortIndices();
  int imin = static_cast<int>(ind[0]) + 1;
  sigma = ew(imin);
  int n = static_cast<int>(A.size1());
  y.allocate(n);
  for (int i = 1; i <= n; ++i) {
    y(i) = ev(i, imin);
  }
}

/** Calculate AplusSigma = A + sigma * I
 *  @param sigma :: The value of the diagonal shift.
 *  @param AplusSigma :: The resulting matrix.
 */
void shiftMatrix(const DoubleFortranMatrix &A, double sigma,
                 DoubleFortranMatrix &AplusSigma) {
  AplusSigma = A;
  auto n = A.len1();
  for (int i = 1; i <= n; ++i) { // for_do(i,1,n)
    AplusSigma(i, i) = AplusSigma(i, i) + sigma;
  }
}

/** Negate a vector
 *  @param v :: A vector.
 */
DoubleFortranVector negative(const DoubleFortranVector &v) {
  DoubleFortranVector neg = v;
  neg *= -1.0;
  return neg;
}

/**  A subroutine to find the optimal beta such that
 *    || d || = Delta, where d = a + beta * b
 *
 *    uses the approach from equation (3.20b),
 *     "Methods for non-linear least squares problems" (2nd edition, 2004)
 *     by Madsen, Nielsen and Tingleff
 *  @param a :: The first vector.
 *  @param b :: The second vector.
 *  @param Delta :: The Delta.
 *  @param beta :: The beta.
 *  @return true if successful
 */
bool findBeta(const DoubleFortranVector &a, const DoubleFortranVector &b,
              double Delta, double &beta) {

  auto c = a.dot(b);

  auto norma2 = pow(NLLS::norm2(a), 2);
  auto normb2 = pow(NLLS::norm2(b), 2);

  double discrim = pow(c, 2) + (normb2) * (pow(Delta, 2) - norma2);
  if (discrim < NLLS::ZERO) {
    return false;
  }

  if (c <= 0) {
    beta = (-c + sqrt(discrim)) / normb2;
  } else {
    beta = (pow(Delta, 2) - norma2) / (c + sqrt(discrim));
  }
  return true;
}

} // namespace

/** Given an indefinite matrix m_A, find a shift sigma
*  such that (A + sigma I) is positive definite.
*  @param sigma :: The result (shift).
*  @param d :: A solution vector to the system of linear equations
*     with the found positive defimnite matrix. The RHS vector is -m_v.
*  @param options :: The options.
*  @return true if successful
*/
bool MoreSorensenMinimizer::getPdShift(double &sigma, DoubleFortranVector &d,
                                       const NLLS::nlls_options &options) {
  int no_shifts = 0;
  bool successful_shift = false;
  while (!successful_shift) {
    shiftMatrix(m_A, sigma, m_AplusSigma);
    successful_shift = solveSpd(m_AplusSigma, negative(m_v), m_LtL, d);
    if (!successful_shift) {
      // We try again with a shifted sigma, but no too many times.
      no_shifts = no_shifts + 1;
      if (no_shifts == 10) {
        return false;
      }
      sigma = sigma + (pow(10.0, no_shifts)) * options.more_sorensen_shift;
    }
  }
  return true;
}

/** Solve the trust-region subproblem using
 *  the method of More and Sorensen
 *
 *  Using the implementation as in Algorithm 7.3.6
 *  of Trust Region Methods
 *
 *  main output  d, the soln to the TR subproblem
 *  @param J :: The Jacobian.
 *  @param f :: The residuals.
 *  @param hf :: The Hessian (sort of).
 *  @param Delta :: The raduis of the trust region.
 *  @param d :: The output vector of corrections to the parameters giving the
 *        solution to the TR subproblem.
 *  @param nd :: The 2-norm of d.
 *  @param options :: The options.
 */
void MoreSorensenMinimizer::solveSubproblem(const DoubleFortranMatrix &J,
                                            const DoubleFortranVector &f,
                                            const DoubleFortranMatrix &hf,
                                            double Delta,
                                            DoubleFortranVector &d, double &nd,
                                            const NLLS::nlls_options &options) {

  // The code finds
  //  d = arg min_p   v^T p + 0.5 * p^T A p
  //       s.t. ||p|| \leq Delta
  //
  // set A and v for the model being considered here...

  // Set A = J^T J
  NLLS::matmultInner(J, m_A);
  // add any second order information...
  // so A = J^T J + HF
  m_A += hf;
  // now form v = J^T f
  NLLS::multJt(J, f, m_v);

  // if scaling needed, do it
  if (options.scale != 0) {
    applyScaling(J, m_A, m_v, m_scale, options);
  }

  auto n = J.len2();
  auto scaleBack = [n, &d, &options, this]() {
    if (options.scale != 0) {
      for (int i = 1; i <= n; ++i) {
        d(i) = d(i) / m_scale(i);
      }
    }
  };

  auto local_ms_shift = options.more_sorensen_shift;
  // d = -A\v
  DoubleFortranVector negv = m_v;
  negv *= -1.0;
  bool matrix_ok = solveSpd(m_A, negv, m_LtL, d);
  double sigma = 0.0;
  if (matrix_ok) {
    // A is symmetric positive definite....
    sigma = NLLS::ZERO;
  } else {
    // shift and try again
    minEigSymm(m_A, sigma, m_y1);
    sigma = -(sigma - local_ms_shift);
    // find a shift that makes (A + sigma I) positive definite
    bool ok = getPdShift(sigma, d, options);
    if (!ok) {
      scaleBack();
      return;
    }
  }

  nd = NLLS::norm2(d);
  if (!std::isfinite(nd)) {
    throw std::runtime_error("Step is NaN or infinite.");
  }

  // now, we're not in the trust region initally, so iterate....
  auto sigma_shift = NLLS::ZERO;
  int no_restarts = 0;
  // set 'small' in the context of the algorithm
  double epsilon =
      std::max(options.more_sorensen_tol * Delta, options.more_sorensen_tiny);
  int it = 1;
  for (; it <= options.more_sorensen_maxits; ++it) {

    if (nd <= Delta + epsilon) {
      // we're within the tr radius
      if (fabs(sigma) < options.more_sorensen_tiny ||
          fabs(nd - Delta) < epsilon) {
        // we're good....exit
        break;
      }
      if (m_y1.len() == n) {
        double alpha = 0.0;
        if (findBeta(d, m_y1, Delta, alpha)) {
          DoubleFortranVector tmp = m_y1;
          tmp *= alpha;
          d += tmp;
        }
      }
      // also good....exit
      break;
    }

    // m_q = R'\d
    // DTRSM( "Left", "Lower", "No Transpose", "Non-unit", n, 1, one, m_LtL, n,
    // m_q, n );
    for (int j = 1; j <= m_LtL.len1(); ++j) {
      for (int k = j + 1; k <= m_LtL.len1(); ++k) {
        m_LtL(j, k) = 0.0;
      }
    }
    m_LtL.solve(d, m_q);

    auto nq = NLLS::norm2(m_q);
    sigma_shift = (pow((nd / nq), 2)) * ((nd - Delta) / Delta);
    if (fabs(sigma_shift) < options.more_sorensen_tiny * fabs(sigma)) {
      if (no_restarts < 1) {
        // find a shift that makes (A + sigma I) positive definite
        bool ok = getPdShift(sigma, d, options);
        if (!ok) {
          break;
        }
        no_restarts = no_restarts + 1;
      } else {
        // we're not going to make progress...jump out
        throw std::runtime_error("Not making progress.");
      }
    } else {
      sigma = sigma + sigma_shift;
    }

    shiftMatrix(m_A, sigma, m_AplusSigma);
    DoubleFortranVector negv = m_v;
    negv *= -1.0;
    bool matrix_ok = solveSpd(m_AplusSigma, negv, m_LtL, d);
    if (!matrix_ok) {
      break;
    }

    nd = NLLS::norm2(d);
  }

  if (it == options.more_sorensen_maxits) {
    // maxits reached, not converged
    throw std::runtime_error("No convergence in maximum number of iterations.");
  }
  scaleBack();
}

/** Implements the abstract method of TrustRegionMinimizer.
 */
void MoreSorensenMinimizer::calculateStep(
    const DoubleFortranMatrix &J, const DoubleFortranVector &f,
    const DoubleFortranMatrix &hf, const DoubleFortranVector &, double Delta,
    DoubleFortranVector &d, double &normd, const NLLS::nlls_options &options) {
  solveSubproblem(J, f, hf, Delta, d, normd, options);
}

} // namespace FuncMinimisers
} // namespace CurveFitting
} // namespace Mantid

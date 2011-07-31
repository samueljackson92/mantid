#ifndef MANTID_ALGORITHMS_PEAKINTEGRATION_H_
#define MANTID_ALGORITHMS_PEAKINTEGRATION_H_

//----------------------------------------------------------------------
// Includes
//----------------------------------------------------------------------
#include "MantidAPI/Algorithm.h"

namespace Mantid
{
namespace Crystal
{
/**
 Find the offsets for each detector

 @author Vickie Lynch, SNS, ORNL
 @date 02/08/2011

 Copyright &copy; 2009 ISIS Rutherford Appleton Laboratory & NScD Oak Ridge National Laboratory

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

 File change history is stored at: <https://svn.mantidproject.org/mantid/trunk/Code/Mantid>
 Code Documentation is available at: <http://doxygen.mantidproject.org>
 */
class DLLExport PeakIntegration: public API::Algorithm
{
public:
  /// Default constructor
  PeakIntegration();
  /// Destructor
  virtual ~PeakIntegration();
  /// Algorithm's name for identification overriding a virtual method
  virtual const std::string name() const { return "PeakIntegration"; }
  /// Algorithm's version for identification overriding a virtual method
  virtual int version() const { return 1; }
  /// Algorithm's category for identification overriding a virtual method
  virtual const std::string category() const { return "Diffraction"; }

private:
  API::MatrixWorkspace_sptr inputW;  ///< A pointer to the input workspace
  API::MatrixWorkspace_sptr outputW; ///< A pointer to the output workspace
  // Overridden Algorithm methods
  void init();
  void exec();
  /// Call Gaussian as a sub-algorithm to fit the peak in a spectrum
  void fitSpectra(const int s, double TOFPeakd, double& I, double& sigI);
  /// Read in all the input parameters
  void retrieveProperties();
  void sumneighbours(std::string det_name, int x0, int y0, int SumX, int SumY, double TOFPeakd, bool &haveMask, double PeakIntensity, int ***mask, int idet);
  int fitneighbours(int ipeak, std::string det_name, int x0, int y0, int idet, double qspan);
  void neighbours(double **matrix, int i, int j, int m, int n, int **mask);
  void cluster(double **matrix, int m, int n, int **mask);
  void smooth(double **matrix, int m, int n, double **smmatrix);
  
  detid2index_map * pixel_to_wi; ///< Map of pixel to workspace index
  int Xmin;        ///< The start of the X range for fitting
  int Xmax;        ///< The end of the X range for fitting
  int Ymin;        ///< The start of the Y range for fitting
  int Ymax;        ///< The end of the Y range for fitting
  int Binmin;        ///< The start of the Bin range for fitting
  int Binmax;        ///< The end of the TOF range for fitting

};

} // namespace Algorithm
} // namespace Mantid

#endif /*MANTID_ALGORITHM_PEAKINTEGRATION_H_*/

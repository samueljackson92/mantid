/*=========================================================================

  Program:   Visualization Toolkit
  Module:    vtkThresholdPolyData.h

  Copyright (c) Ken Martin, Will Schroeder, Bill Lorensen
  All rights reserved.
  See Copyright.txt or http://www.kitware.com/Copyright.htm for details.

     This software is distributed WITHOUT ANY WARRANTY; without even
     the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
     PURPOSE.  See the above copyright notice for more information.

=========================================================================*/
/**
 * @class   vtkThresholdPolyData
 * @brief   extracts cells where scalar value in cell satisfies threshold criterion
 *
 * vtkThresholdPolyData is a filter that extracts cells from any dataset type that
 * satisfy a threshold criterion. A cell satisfies the criterion if the
 * scalar value of (every or any) point satisfies the criterion. The
 * criterion can take three forms: 1) greater than a particular value; 2)
 * less than a particular value; or 3) between two values. The output of this
 * filter is an unstructured grid.
 *
 * Note that scalar values are available from the point and cell attribute
 * data.  By default, point data is used to obtain scalars, but you can
 * control this behavior. See the AttributeMode ivar below.
 *
 * By default only the first scalar value is used in the decision. Use the ComponentMode
 * and SelectedComponent ivars to control this behavior.
 *
 * @sa
 * vtkThresholdPolyDataPoints vtkThresholdPolyDataTextureCoords
*/

#ifndef vtkThresholdPolyData_h
#define vtkThresholdPolyData_h

#include "vtkFiltersCoreModule.h" // For export macro
#include "vtkPolyDataAlgorithm.h"

class vtkDataArray;
class vtkIdList;

class VTKFILTERSCORE_EXPORT vtkThresholdPolyData : public vtkPolyDataAlgorithm
{
public:
  static vtkThresholdPolyData *New();
  vtkTypeMacro(vtkThresholdPolyData,vtkPolyDataAlgorithm);
  void PrintSelf(ostream& os, vtkIndent indent) override;
  /**
   * Criterion is cells whose scalars are between lower and upper thresholds
   * (inclusive of the end values).
   */
  void ThresholdBetween(double lower, double upper);

  //@{
  /**
   * Get the Upper and Lower thresholds.
   */
  vtkGetMacro(UpperThreshold,double);
  vtkGetMacro(LowerThreshold,double);
  //@}

  vtkThresholdPolyData(const vtkThresholdPolyData&) = delete;
  void operator=(const vtkThresholdPolyData&) = delete;

protected:
  vtkThresholdPolyData();
  ~vtkThresholdPolyData() override;

  // Usual data generation method
  int RequestData(vtkInformation *, vtkInformationVector **, vtkInformationVector *) override;

  int FillInputPortInformation(int port, vtkInformation *info) override;
  bool Between(double s);
  
  double LowerThreshold;
  double UpperThreshold;
};

#endif

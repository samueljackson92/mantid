/*=========================================================================

  Program:   Visualization Toolkit
  Module:    vtkThresholdPolyData.cxx

  Copyright (c) Ken Martin, Will Schroeder, Bill Lorensen
  All rights reserved.
  See Copyright.txt or http://www.kitware.com/Copyright.htm for details.

     This software is distributed WITHOUT ANY WARRANTY; without even
     the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
     PURPOSE.  See the above copyright notice for more information.

=========================================================================*/
#include "vtkThresholdPolyData.h"

#include "vtkCell.h"
#include "vtkCellData.h"
#include "vtkIdList.h"
#include "vtkInformation.h"
#include "vtkInformationVector.h"
#include "vtkObjectFactory.h"
#include "vtkPointData.h"
#include "vtkPolyData.h"
#include "vtkStreamingDemandDrivenPipeline.h"
#include "vtkMath.h"

#include <algorithm>

vtkStandardNewMacro(vtkThresholdPolyData);

// Construct with lower threshold=0, upper threshold=1, and threshold
// function=upper AllScalars=1.
vtkThresholdPolyData::vtkThresholdPolyData()
{
  this->LowerThreshold         = 0.0;
  this->UpperThreshold         = 1.0;
  // by default process active point scalars
  this->SetInputArrayToProcess(0,0,0,vtkDataObject::FIELD_ASSOCIATION_POINTS,
                               vtkDataSetAttributes::SCALARS);
}

vtkThresholdPolyData::~vtkThresholdPolyData() = default;

// Criterion is cells whose scalars are between lower and upper thresholds.
void vtkThresholdPolyData::ThresholdBetween(double lower, double upper)
{
  if ( this->LowerThreshold != lower || this->UpperThreshold != upper)
  {
    this->LowerThreshold = lower;
    this->UpperThreshold = upper;
    this->Modified();
  }
}

int vtkThresholdPolyData::RequestData(
  vtkInformation *vtkNotUsed(request),
  vtkInformationVector **inputVector,
  vtkInformationVector *outputVector)
{
  // get the info objects
  vtkInformation *inInfo = inputVector[0]->GetInformationObject(0);
  vtkInformation *outInfo = outputVector->GetInformationObject(0);

  // get the input and output
  vtkPolyData *input = vtkPolyData::SafeDownCast(inInfo->Get(vtkDataObject::DATA_OBJECT()));
  vtkPolyData *output = vtkPolyData::SafeDownCast(outInfo->Get(vtkDataObject::DATA_OBJECT()));

  vtkPointData *pd=input->GetPointData();
  vtkPointData *outPD=output->GetPointData();

  vtkDebugMacro(<< "Executing threshold filter");

  vtkDataArray *inScalars = this->GetInputArrayToProcess(0,inputVector);

  if (!inScalars)
  {
    vtkDebugMacro(<<"No scalar data to threshold");
    return 1;
  }

  outPD->CopyGlobalIdsOn();
  outPD->CopyAllocate(pd);

  vtkIdType numPts = input->GetNumberOfPoints();
  output->Allocate(input->GetNumberOfPoints());

  vtkPoints *oldPoints = input->GetPoints();
  vtkPoints *newPoints = vtkPoints::New();
  newPoints->SetDataType(oldPoints->GetDataType());
  newPoints->Allocate(numPts);

  // are we using pointScalars?
  // int fieldAssociation = this->GetInputArrayAssociation(0, inputVector);

  // Check that the scalars of each cell satisfy the threshold criterion
  for (vtkIdType ptId=0; ptId < input->GetNumberOfPoints(); ++ptId)
  {
    bool keepPoint = this->Between(inScalars->GetComponent(ptId, 0));
    if(keepPoint)
    {
      double x[3];
      input->GetPoint(ptId, x);
      vtkIdType newId = newPoints->InsertNextPoint(x);
      outPD->CopyData(pd,ptId,newId);
    }
  } // for all points

  vtkDebugMacro(<< "Extracted " << output->GetNumberOfPoints() << " points.");
  output->SetPoints(newPoints);
  newPoints->Delete();
  output->Squeeze();
  return 1;
}

int vtkThresholdPolyData::FillInputPortInformation(int, vtkInformation *info)
{
  info->Set(vtkAlgorithm::INPUT_REQUIRED_DATA_TYPE(), "vtkPolyData");
  return 1;
}

bool vtkThresholdPolyData::Between(double s)
{
  return s >= this->LowerThreshold && s <= this->UpperThreshold;
}

void vtkThresholdPolyData::PrintSelf(ostream& os, vtkIndent indent)
{
  this->Superclass::PrintSelf(os,indent);
  os << indent << "Threshold Between\n";
  os << indent << "Lower Threshold: " << this->LowerThreshold << "\n";
  os << indent << "Upper Threshold: " << this->UpperThreshold << "\n";
}

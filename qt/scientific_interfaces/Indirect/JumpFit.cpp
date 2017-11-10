#include "JumpFit.h"
#include "../General/UserInputValidator.h"
#include "MantidAPI/AlgorithmManager.h"
#include "MantidAPI/FunctionFactory.h"
#include "MantidAPI/IFunction.h"
#include "MantidAPI/ITableWorkspace.h"
#include "MantidAPI/Run.h"
#include "MantidAPI/TextAxis.h"

#include <boost/lexical_cast.hpp>
#include <string>

using namespace Mantid::API;

namespace MantidQt {
namespace CustomInterfaces {
namespace IDA {

JumpFit::JumpFit(QWidget *parent)
    : IndirectDataAnalysisTab(parent), m_jfTree(nullptr) {
  m_uiForm.setupUi(parent);
}

void JumpFit::setup() {
  // Create range selector
  auto qRangeSelector = m_uiForm.ppPlotTop->addRangeSelector("JumpFitQ");
  connect(qRangeSelector, SIGNAL(selectionChangedLazy(double, double)), this,
          SLOT(qRangeChanged(double, double)));

  // Add the properties browser to the ui form
  m_jfTree = new QtTreePropertyBrowser();
  m_jfTree->setFactoryForManager(m_dblManager, m_dblEdFac);
  m_uiForm.treeSpace->addWidget(m_jfTree);

  // Fitting range
  m_properties["QMin"] = m_dblManager->addProperty("QMin");
  m_properties["QMax"] = m_dblManager->addProperty("QMax");

  m_dblManager->setDecimals(m_properties["QMin"], NUM_DECIMALS);
  m_dblManager->setDecimals(m_properties["QMax"], NUM_DECIMALS);

  m_jfTree->addProperty(m_properties["QMin"]);
  m_jfTree->addProperty(m_properties["QMax"]);

  // Fitting function
  m_properties["FitFunction"] = m_grpManager->addProperty("Fitting Parameters");
  m_jfTree->addProperty(m_properties["FitFunction"]);

  m_uiForm.cbWidth->setEnabled(false);

  // Connect data selector to handler method
  connect(m_uiForm.dsSample, SIGNAL(dataReady(const QString &)), this,
          SLOT(handleSampleInputReady(const QString &)));
  // Connect width selector to handler method
  connect(m_uiForm.cbWidth, SIGNAL(currentIndexChanged(const QString &)), this,
          SLOT(handleWidthChange(const QString &)));

  // Update fit parameters in browser when function is selected
  connect(m_uiForm.cbFunction, SIGNAL(currentIndexChanged(const QString &)),
          this, SLOT(fitFunctionSelected(const QString &)));

  connect(m_dblManager, SIGNAL(valueChanged(QtProperty *, double)), this,
          SLOT(updateProperties(QtProperty *, double)));

  fitFunctionSelected(m_uiForm.cbFunction->currentText());

  // Update plot Guess
  connect(m_uiForm.ckPlotGuess, SIGNAL(stateChanged(int)), this,
          SLOT(plotGuess()));

  connect(m_dblManager, SIGNAL(propertyChanged(QtProperty *)), this,
          SLOT(plotGuess()));

  // Handle plotting and saving
  connect(m_uiForm.pbSave, SIGNAL(clicked()), this, SLOT(saveClicked()));
  connect(m_uiForm.pbPlot, SIGNAL(clicked()), this, SLOT(plotClicked()));
  connect(m_uiForm.pbPlotPreview, SIGNAL(clicked()), this,
          SLOT(plotCurrentPreview()));
}

/**
 * Validate the form to check the program can be run
 *
 * @return :: Whether the form was valid
 */
bool JumpFit::validate() {
  UserInputValidator uiv;
  uiv.checkDataSelectorIsValid("Sample", m_uiForm.dsSample);

  // this workspace doesn't have any valid widths
  if (m_spectraList.size() == 0) {
    uiv.addErrorMessage(
        "Input workspace doesn't appear to contain any width data.");
  }

  QString errors = uiv.generateErrorMessage();
  if (!errors.isEmpty()) {
    emit showMessageBox(errors);
    return false;
  }

  return true;
}

/**
 * Collect the settings on the GUI and build a python
 * script that runs JumpFit
 */
void JumpFit::run() {
  // Do noting with invalid data
  if (!m_uiForm.dsSample->isValid())
    return;

  if (m_batchAlgoRunner->queueLength() > 0)
    return;

  // Fit function to use
  const QString functionName = m_uiForm.cbFunction->currentText();
  // Setup fit algorithm
  m_fitAlg = createFitAlgorithm(createFunction(functionName));

  m_batchAlgoRunner->addAlgorithm(m_fitAlg);
  // Connect algorithm runner to completion handler function
  connect(m_batchAlgoRunner, SIGNAL(batchComplete(bool)), this,
          SLOT(fitAlgDone(bool)));
  m_batchAlgoRunner->executeBatchAsync();
}

/**
 * Handles the JumpFit algorithm finishing, used to plot fit in miniplot.
 *
 * @param error True if the algorithm failed, false otherwise
 */
void JumpFit::fitAlgDone(bool error) {
  disconnect(m_batchAlgoRunner, SIGNAL(batchComplete(bool)), this,
             SLOT(fitAlgDone(bool)));
  // Ignore errors
  if (error)
    return;
  m_uiForm.pbPlot->setEnabled(true);
  m_uiForm.pbSave->setEnabled(true);
  std::string outName = m_fitAlg->getPropertyValue("Output");

  // Get output workspace name
  std::string outWsName = outName + "_Workspace";
  IndirectDataAnalysisTab::updatePlot(outWsName, m_uiForm.ppPlotTop,
                                      m_uiForm.ppPlotBottom);

  // Update parameters in UI
  std::string paramTableName = outName + "_Parameters";

  ITableWorkspace_sptr paramTable =
      AnalysisDataService::Instance().retrieveWS<ITableWorkspace>(
          paramTableName);
  const auto plotResult = m_uiForm.ckPlotGuess->isChecked();
  if (plotResult) {
    m_uiForm.ckPlotGuess->setChecked(false);
  }
  for (auto it = m_properties.begin(); it != m_properties.end(); ++it) {
    const QString &propName(it.key());
    if (propName.startsWith("parameter_")) {
      size_t row(0), col(0);
      paramTable->find(propName.split("_")[1].toStdString(), row, col);
      col++;
      double value = paramTable->cell<double>(row, col);
      m_dblManager->setValue(m_properties[propName], value);
    }
  }
}

/**
 * Set the data selectors to use the default save directory
 * when browsing for input files.
 *
 * @param settings :: The current settings
 */
void JumpFit::loadSettings(const QSettings &settings) {
  m_uiForm.dsSample->readSettings(settings.group());
}

/**
 * Plots the loaded file to the miniplot and sets the guides
 * and the range
 *
 * @param filename :: The name of the workspace to plot
 */
void JumpFit::handleSampleInputReady(const QString &filename) {
  // Scale to convert to HWHM
  QString sample = filename + "_HWHM";
  IAlgorithm_sptr scaleAlg = AlgorithmManager::Instance().create("Scale");
  scaleAlg->initialize();
  scaleAlg->setProperty("InputWorkspace", filename.toStdString());
  scaleAlg->setProperty("OutputWorkspace", sample.toStdString());
  scaleAlg->setProperty("Factor", 0.5);
  scaleAlg->execute();

  auto ws =
      Mantid::API::AnalysisDataService::Instance().retrieveWS<MatrixWorkspace>(
          sample.toStdString());
  setInputWorkspace(ws);

  findAllWidths(inputWorkspace());

  auto qRangeSelector = m_uiForm.ppPlotTop->getRangeSelector("JumpFitQ");

  if (m_spectraList.size() > 0) {
    m_uiForm.cbWidth->setEnabled(true);
    std::string currentWidth = m_uiForm.cbWidth->currentText().toStdString();
    setSelectedSpectrum(m_spectraList[currentWidth]);
    m_uiForm.ppPlotBottom->clear();
    plotInput(m_uiForm.ppPlotTop);

    QPair<double, double> res;
    QPair<double, double> range = m_uiForm.ppPlotTop->getCurveRange("Sample");

    // Use the values from the instrument parameter file if we can
    if (getResolutionRangeFromWs(sample, res))
      setRangeSelector(qRangeSelector, m_properties["QMin"],
                       m_properties["QMax"], res);
    else
      setRangeSelector(qRangeSelector, m_properties["QMin"],
                       m_properties["QMax"], range);

    setPlotPropertyRange(qRangeSelector, m_properties["QMin"],
                         m_properties["QMax"], range);
  } else {
    m_uiForm.cbWidth->setEnabled(false);
    emit showMessageBox("Workspace doesn't appear to contain any width data");
  }
}

/**
 * Find all of the spectra in the workspace that have width data
 *
 * @param ws :: The workspace to search
 */
void JumpFit::findAllWidths(Mantid::API::MatrixWorkspace_const_sptr ws) {
  m_uiForm.cbWidth->blockSignals(true);
  m_uiForm.cbWidth->clear();
  m_spectraList.clear();

  for (size_t i = 0; i < ws->getNumberHistograms(); ++i) {
    auto axis = dynamic_cast<Mantid::API::TextAxis *>(ws->getAxis(1));
    if (!axis)
      return;

    std::string title = axis->label(i);

    // check if the axis labels indicate this spectrum is width data
    size_t qLinesWidthIndex = title.find(".Width");
    size_t convFitWidthIndex = title.find(".FWHM");

    bool qLinesWidth = qLinesWidthIndex != std::string::npos;
    bool convFitWidth = convFitWidthIndex != std::string::npos;

    // if we get a match, add this spectrum to the combobox
    if (convFitWidth || qLinesWidth) {
      std::string cbItemName = "";
      size_t substrIndex = 0;

      if (qLinesWidth) {
        substrIndex = qLinesWidthIndex;
      } else if (convFitWidth) {
        substrIndex = convFitWidthIndex;
      }

      cbItemName = title.substr(0, substrIndex);
      m_spectraList[cbItemName] = static_cast<int>(i);
      m_uiForm.cbWidth->addItem(QString(cbItemName.c_str()));

      // display widths f1.f1, f2.f1 and f2.f2
      if (m_uiForm.cbWidth->count() == 3) {
        return;
      }
    }
  }
  m_uiForm.cbWidth->blockSignals(false);
}

/**
 * Plots the loaded file to the miniplot when the selected spectrum changes
 *
 * @param text :: The name spectrum index to plot
 */
void JumpFit::handleWidthChange(const QString &text) {
  QString sampleName = (m_uiForm.dsSample->getCurrentDataName() + "_HWHM");

  if (!sampleName.isEmpty() && m_spectraList.size() > 0) {
    if (validate()) {
      m_uiForm.ppPlotTop->clear();
      m_uiForm.ppPlotTop->addSpectrum("Sample", sampleName,
                                      m_spectraList[text.toStdString()]);
    }
  }
}

/**
 * Updates the property manager when the range selector is moved on the mini
 *plot.
 *
 * @param min :: The new value of the lower guide
 * @param max :: The new value of the upper guide
 */
void JumpFit::qRangeChanged(double min, double max) {
  m_dblManager->setValue(m_properties["QMin"], min);
  m_dblManager->setValue(m_properties["QMax"], max);
}

/**
 * Handles when properties in the property manager are updated.
 *
 * @param prop :: The property being updated
 * @param val :: The new value for the property
 */
void JumpFit::updateProperties(QtProperty *prop, double val) {
  UNUSED_ARG(val);

  auto qRangeSelector = m_uiForm.ppPlotTop->getRangeSelector("JumpFitQ");

  if (prop == m_properties["QMin"] || prop == m_properties["QMax"]) {
    auto bounds = qMakePair(m_dblManager->value(m_properties["QMin"]),
                            m_dblManager->value(m_properties["QMax"]));
    setRangeSelector(qRangeSelector, m_properties["QMin"], m_properties["QMax"],
                     bounds);
  }
}

/**
 * Gets a list of parameters for a given fit function.
 *
 * @return List of parameters
 */
QStringList JumpFit::getFunctionParameters(const QString &functionName) {
  QStringList parameters;

  IFunction_sptr func =
      FunctionFactory::Instance().createFunction(functionName.toStdString());

  for (size_t i = 0; i < func->nParams(); i++)
    parameters << QString::fromStdString(func->parameterName(i));

  return parameters;
}

/**
 * Handles a new fit function being selected.
 *
 * @param functionName Name of new fit function
 */
void JumpFit::fitFunctionSelected(const QString &functionName) {
  const auto plotGuess = m_uiForm.ckPlotGuess->isChecked();
  if (plotGuess) {
    m_uiForm.ckPlotGuess->setChecked(false);
  }
  // Remove current parameter elements
  for (auto it = m_properties.begin(); it != m_properties.end();) {
    if (it.key().startsWith("parameter_")) {
      delete it.value();
      it = m_properties.erase(it);
    } else {
      ++it;
    }
  }

  // Add new parameter elements
  QStringList parameters = getFunctionParameters(functionName);
  for (auto it = parameters.begin(); it != parameters.end(); ++it) {
    QString name = "parameter_" + *it;
    m_properties[name] = m_dblManager->addProperty(*it);
    m_dblManager->setValue(m_properties[name], 1.0);
    m_properties["FitFunction"]->addSubProperty(m_properties[name]);
  }

  clearPlot();
  if (plotGuess) {
    m_uiForm.ckPlotGuess->setChecked(true);
  }
}

/**
 * clears the previous plot curves and readds sample
 */
void JumpFit::clearPlot() {
  m_uiForm.ppPlotTop->clear();
  const std::string sampleName =
      (m_uiForm.dsSample->getCurrentDataName().toStdString());
  if (sampleName.compare("") != 0) {
    MatrixWorkspace_sptr sample =
        AnalysisDataService::Instance().retrieveWS<MatrixWorkspace>(sampleName +
                                                                    "_HWHM");
    if (sample && m_spectraList.size() > 0) {
      m_uiForm.cbWidth->setEnabled(true);

      std::string currentWidth = m_uiForm.cbWidth->currentText().toStdString();

      m_uiForm.ppPlotTop->clear();
      m_uiForm.ppPlotTop->addSpectrum("Sample", sample,
                                      m_spectraList[currentWidth]);
    }
  }
}

void JumpFit::plotGuess() {
  // Do nothing if there is not a sample
  if (m_uiForm.dsSample->isValid() && m_uiForm.ckPlotGuess->isChecked()) {
    const QString functionName = m_uiForm.cbFunction->currentText();
    IndirectDataAnalysisTab::plotGuess(m_uiForm.ppPlotTop,
                                       createFunction(functionName));
    deletePlotGuessWorkspaces(false);
  } else {
    m_uiForm.ppPlotTop->removeSpectrum("Guess");
    m_uiForm.ckPlotGuess->setChecked(false);
    deletePlotGuessWorkspaces(true);
  }
}

IAlgorithm_sptr JumpFit::createFitAlgorithm(IFunction_sptr func) {
  std::string widthText = m_uiForm.cbWidth->currentText().toStdString();
  int width = m_spectraList[widthText];
  const auto sample =
      m_uiForm.dsSample->getCurrentDataName().toStdString() + "_HWHM";
  const auto startX = m_dblManager->value(m_properties["QMin"]);
  const auto endX = m_dblManager->value(m_properties["QMax"]);

  auto fitAlg = AlgorithmManager::Instance().create("Fit");
  fitAlg->initialize();
  fitAlg->setProperty("Function", func->asString());
  fitAlg->setProperty("InputWorkspace", sample);
  fitAlg->setProperty("WorkspaceIndex", width);
  fitAlg->setProperty("IgnoreInvalidData", true);
  fitAlg->setProperty("StartX", startX);
  fitAlg->setProperty("EndX", endX);
  fitAlg->setProperty("CreateOutput", true);
  fitAlg->setProperty("Output", "__PlotGuessData");
  return fitAlg;
}

/**
 * Creates a function string to be used in fitting
 */
IFunction_sptr JumpFit::createFunction(const QString &functionName) {
  QString functionString = "name=" + functionName;

  // Build function string
  QStringList parameters = getFunctionParameters(functionName);
  for (auto it = parameters.begin(); it != parameters.end(); ++it) {
    QString parameterName = *it;

    // Get the value form double manager
    QString name = "parameter_" + *it;
    double value = m_dblManager->value(m_properties[name]);
    QString parameterValue = QString::number(value);

    functionString += "," + parameterName + "=" + parameterValue;
  }
  return FunctionFactory::Instance().createInitialized(
      functionString.toStdString());
}

/**
 * Remove PlotGuess related workspaces from the ADS
 * @param removePlotGuess :: Removes the plotGuess data and not just the
 * unwanted workspaces
 */
void JumpFit::deletePlotGuessWorkspaces(const bool &removePlotGuess) {
  auto deleteAlg = AlgorithmManager::Instance().create("DeleteWorkspace");
  deleteAlg->initialize();
  deleteAlg->setLogging(false);
  if (removePlotGuess) {
    if (AnalysisDataService::Instance().doesExist(
            "__PlotGuessData_Workspace")) {
      deleteAlg->setProperty("Workspace", "__PlotGuessData_Workspace");
      deleteAlg->execute();
    }
  }
  if (AnalysisDataService::Instance().doesExist("__PlotGuessData_Parameters")) {
    deleteAlg->setProperty("Workspace", "__PlotGuessData_Parameters");
    deleteAlg->execute();
  }
  if (AnalysisDataService::Instance().doesExist(
          "__PlotGuessData_NormalisedCovarianceMatrix")) {
    deleteAlg->setProperty("Workspace",
                           "__PlotGuessData_NormalisedCovarianceMatrix");
    deleteAlg->execute();
  }
}

/**
 * Handles mantid plotting
 */
void JumpFit::plotClicked() {
  std::string outWsName = m_fitAlg->getPropertyValue("Output") + "_Workspace";
  checkADSForPlotSaveWorkspace(outWsName, true);
  plotSpectrum(QString::fromStdString(outWsName), 0, 2);
}

/**
 * Handles saving of workspace
 */
void JumpFit::saveClicked() {
  std::string outWsName = m_fitAlg->getPropertyValue("Output") + "_Workspace";
  checkADSForPlotSaveWorkspace(outWsName, false);
  addSaveWorkspaceToQueue(QString::fromStdString(outWsName));
  m_batchAlgoRunner->executeBatchAsync();
}

} // namespace IDA
} // namespace CustomInterfaces
} // namespace MantidQt

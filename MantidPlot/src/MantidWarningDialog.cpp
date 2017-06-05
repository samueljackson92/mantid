#include "MantidWarningDialog.h"
#include "MantidKernel/Logger.h"

#include <iostream>

namespace {
/// static logger
Mantid::Kernel::Logger g_log("WarningDialog");
}


MantidWarningDialog::MantidWarningDialog(QWidget *parent)
    : QMessageBox(parent) {}

MantidWarningDialog::MantidWarningDialog(Icon icon, const QString &title,
                                         const QString &text,
                                         StandardButtons buttons,
                                         QWidget *parent, Qt::WindowFlags f)
    : QMessageBox(icon, title, text, buttons, parent, f) {}

MantidWarningDialog::MantidWarningDialog(const QString &title,
                                         const QString &text, Icon icon,
                                         int button0, int button1, int button2,
                                         QWidget *parent, Qt::WindowFlags f)
    : QMessageBox(title, text, icon, button0, button1, button2, parent) {}

QMessageBox::StandardButton
MantidWarningDialog::warning(QWidget *parent, const QString &title,
                             const QString &text,
                             QMessageBox::StandardButtons buttons,
                             QMessageBox::StandardButton defaultButton) {
//#ifdef LOGMODALS
  g_log.warning() << text.toStdString() << std::endl;
//#endif
  return QMessageBox::warning(parent, title, text, buttons, defaultButton);
}

QMessageBox::StandardButton
MantidWarningDialog::critical(QWidget *parent, const QString &title,
                              const QString &text,
                              QMessageBox::StandardButtons buttons,
                              QMessageBox::StandardButton defaultButton) {
//#ifdef LOGMODALS
  g_log.error() << text.toStdString() << std::endl;
//#endif
  return QMessageBox::critical(parent, title, text, buttons, defaultButton);
}

QMessageBox::StandardButton
MantidWarningDialog::information(QWidget *parent, const QString &title,
                                 const QString &text,
                                 QMessageBox::StandardButtons buttons,
                                 QMessageBox::StandardButton defaultButton) {
//#ifdef LOGMODALS
  g_log.notice() << text.toStdString() << std::endl;
//#endif
  return QMessageBox::information(parent, title, text, buttons, defaultButton);
}

QMessageBox::StandardButton
MantidWarningDialog::question(QWidget *parent, const QString &title,
                              const QString &text,
                              QMessageBox::StandardButtons buttons,
                              QMessageBox::StandardButton defaultButton) {
//#ifdef LOGMODALS
  g_log.notice() << text.toStdString() << std::endl;
//#endif
  return QMessageBox::question(parent, title, text, buttons, defaultButton);
}

int MantidWarningDialog::information(QWidget *parent, const QString &title,
                                     const QString &text, int button0,
                                     int button1, int button2) {
//#ifdef LOGMODALS
  g_log.notice() << text.toStdString() << std::endl;
//#endif
  return QMessageBox::information(parent, title, text, button0, button1,
                                  button2);
}

int MantidWarningDialog::information(QWidget *parent, const QString &title,
                                     const QString &text,
                                     const QString &button0Text,
                                     const QString &button1Text,
                                     const QString &button2Text,
                                     int defaultButtonNumber,
                                     int escapeButtonNumber) {
//#ifdef LOGMODALS
  g_log.notice() << text.toStdString() << std::endl;
//#endif
  return QMessageBox::information(parent, title, text, button0Text, button1Text,
                                  button2Text, defaultButtonNumber,
                                  escapeButtonNumber);
}

int MantidWarningDialog::question(QWidget *parent, const QString &title,
                                  const QString &text, int button0, int button1,
                                  int button2) {
//#ifdef LOGMODALS
  g_log.notice() << text.toStdString() << std::endl;
//#endif
  return QMessageBox::question(parent, title, text, button0, button1, button2);
}

int MantidWarningDialog::question(QWidget *parent, const QString &title,
                                  const QString &text,
                                  const QString &button0Text,
                                  const QString &button1Text,
                                  const QString &button2Text,
                                  int defaultButtonNumber,
                                  int escapeButtonNumber) {
//#ifdef LOGMODALS
  g_log.notice() << text.toStdString() << std::endl;
//#endif
  return QMessageBox::question(parent, title, text, button0Text, button1Text,
                               button2Text, defaultButtonNumber,
                               escapeButtonNumber);
}

int MantidWarningDialog::warning(QWidget *parent, const QString &title,
                                 const QString &text, int button0, int button1,
                                 int button2) {
//#ifdef LOGMODALS
  g_log.warning() << text.toStdString() << std::endl;
//#endif
  return QMessageBox::warning(parent, title, text, button0, button1, button2);
}

int MantidWarningDialog::warning(QWidget *parent, const QString &title,
                                 const QString &text,
                                 const QString &button0Text,
                                 const QString &button1Text,
                                 const QString &button2Text,
                                 int defaultButtonNumber,
                                 int escapeButtonNumber) {
//#ifdef LOGMODALS
  g_log.warning() << text.toStdString() << std::endl;
//#endif
  return QMessageBox::warning(parent, title, text, button0Text, button1Text,
                              button2Text, defaultButtonNumber,
                              escapeButtonNumber);
}

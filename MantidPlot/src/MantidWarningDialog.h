#ifndef MANTIDWARNINGDIALOG_H
#define MANTIDWARNINGDIALOG_H

#include <QMessageBox>

class MantidWarningDialog : public QMessageBox {
  Q_OBJECT

public:
  MantidWarningDialog(QWidget *parent = 0);

  MantidWarningDialog(Icon icon, const QString &title, const QString &text,
                      StandardButtons buttons = NoButton, QWidget *parent = 0,
                      Qt::WindowFlags f = Qt::Dialog |
                                          Qt::MSWindowsFixedSizeDialogHint);

  MantidWarningDialog(const QString &title, const QString &text, Icon icon,
                      int button0, int button1, int button2,
                      QWidget *parent = 0,
                      Qt::WindowFlags f = Qt::Dialog |
                                          Qt::MSWindowsFixedSizeDialogHint);

  static StandardButton warning(QWidget *parent, const QString &title,
                                const QString &text,
                                StandardButtons buttons = Ok,
                                StandardButton defaultButton = NoButton);

  static StandardButton critical(QWidget *parent, const QString &title,
                                 const QString &text,
                                 StandardButtons buttons = Ok,
                                 StandardButton defaultButton = NoButton);

  static StandardButton information(QWidget *parent, const QString &title,
                                    const QString &text,
                                    StandardButtons buttons = Ok,
                                    StandardButton defaultButton = NoButton);

  static StandardButton question(QWidget *parent, const QString &title,
                                 const QString &text,
                                 StandardButtons buttons = Ok,
                                 StandardButton defaultButton = NoButton);

  // Qt says: the following functions are obsolete:

  static int information(QWidget *parent, const QString &title,
                         const QString &text, int button0, int button1 = 0,
                         int button2 = 0);
  static int information(QWidget *parent, const QString &title,
                         const QString &text, const QString &button0Text,
                         const QString &button1Text = QString(),
                         const QString &button2Text = QString(),
                         int defaultButtonNumber = 0,
                         int escapeButtonNumber = -1);
  inline static StandardButton
  information(QWidget *parent, const QString &title, const QString &text,
              StandardButton button0, StandardButton button1 = NoButton) {
    return information(parent, title, text, StandardButtons(button0), button1);
  }

   static int question(QWidget *parent, const QString &title,
                      const QString &text, int button0, int button1 = 0,
                      int button2 = 0);
   static int question(QWidget *parent, const QString &title,
                      const QString &text, const QString &button0Text,
                      const QString &button1Text = QString(),
                      const QString &button2Text = QString(),
                      int defaultButtonNumber = 0, int escapeButtonNumber =
                      -1);
   inline static int question(QWidget *parent, const QString &title,
                             const QString &text, StandardButton button0,
                             StandardButton button1) {
    return question(parent, title, text, StandardButtons(button0), button1);
  }

   static int warning(QWidget *parent, const QString &title, const QString
   &text,
                     int button0, int button1, int button2 = 0);
   static int warning(QWidget *parent, const QString &title, const QString
   &text,
                     const QString &button0Text,
                     const QString &button1Text = QString(),
                     const QString &button2Text = QString(),
                     int defaultButtonNumber = 0, int escapeButtonNumber =
                     -1);
   inline static int warning(QWidget *parent, const QString &title,
                            const QString &text, StandardButton button0,
                            StandardButton button1) {
    return warning(parent, title, text, StandardButtons(button0), button1);
  }

  // static int critical(QWidget *parent, const QString &title,
  //                    const QString &text, int button0, int button1,
  //                    int button2 = 0);
  // static int critical(QWidget *parent, const QString &title,
  //                    const QString &text, const QString &button0Text,
  //                    const QString &button1Text = QString(),
  //                    const QString &button2Text = QString(),
  //                    int defaultButtonNumber = 0, int escapeButtonNumber =
  //                    -1);
  // inline static int critical(QWidget *parent, const QString &title,
  //                           const QString &text, StandardButton button0,
  //                           StandardButton button1) {
  //  return critical(parent, title, text, StandardButtons(button0), button1);
  //}
};

#endif // MANTIDWARNINGDIALOG_H

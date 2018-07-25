#include "MantidQtWidgets/Common/HintingLineEdit.h"

#include <boost/algorithm/string.hpp>
#include <QKeyEvent>
#include <QLabel>
#include <QStyle>
#include <QToolTip>
#include <boost/algorithm/string.hpp>

namespace MantidQt {
namespace MantidWidgets {
HintingLineEdit::HintingLineEdit(
    QWidget *parent, const std::map<std::string, std::string> &hints)
    : QLineEdit(parent), m_hints(hints), m_dontComplete(false) {
  m_hintLabel = new QLabel(this, Qt::ToolTip);
  m_hintLabel->setMargin(1 +
                         style()->pixelMetric(QStyle::PM_ToolTipLabelFrameWidth,
                                              nullptr, m_hintLabel));
  m_hintLabel->setFrameStyle(QFrame::StyledPanel);
  m_hintLabel->setAlignment(Qt::AlignLeft);
  m_hintLabel->setWordWrap(true);
  m_hintLabel->setIndent(1);
  m_hintLabel->setAutoFillBackground(true);
  m_hintLabel->setForegroundRole(QPalette::ToolTipText);
  m_hintLabel->setBackgroundRole(QPalette::ToolTipBase);
  m_hintLabel->ensurePolished();

  connect(this, SIGNAL(textEdited(const QString &)), this,
          SLOT(updateHints(const QString &)));
  connect(this, SIGNAL(editingFinished()), this, SLOT(hideHints()));
}

HintingLineEdit::~HintingLineEdit() {}

/** Handle a key press event.

    @param e : A pointer to the event
 */
void HintingLineEdit::keyPressEvent(QKeyEvent *e) {
  m_dontComplete = (e->key() == Qt::Key_Backspace ||
                    e->key() == Qt::Key_Delete || e->key() == Qt::Key_Space);

  if (e->key() == Qt::Key_Up) {
    prevSuggestion();
    return;
  }

  if (e->key() == Qt::Key_Down) {
    nextSuggestion();
    return;
  }
  QLineEdit::keyPressEvent(e);
}

/** Rebuild a list of hints whenever the user edits the text, and use the hints
    to make auto completion suggestions.

    @param text : The new contents of the QLineEdit
 */
void HintingLineEdit::updateHints(const QString &text) {
  const size_t curPos = (size_t)cursorPosition();
  const std::string line = text.toStdString();

  // Get everything before the cursor
  std::string prefix = line.substr(0, curPos);

  // Now remove everything before the last ',' to give us the current word
  std::size_t startPos = prefix.find_last_of(",");
  if (startPos != std::string::npos)
    prefix = prefix.substr(startPos + 1, prefix.size() - (startPos + 1));

  // Remove any leading or trailing whitespace
  boost::trim(prefix);

  // Set the current key/prefix
  m_curKey = prefix;

  // Update our current list of matches
  updateMatches();

  // Show the potential matches in a tooltip
  showToolTip();

  // Suggest one of them to the user via auto-completion
  insertSuggestion();
}

/** Hides the list of hints
*/
void HintingLineEdit::hideHints() { m_hintLabel->hide(); }

/** Updates the list of hints matching the user's current input */
void HintingLineEdit::updateMatches() {
  m_curMatch.clear();
  m_matches.clear();

  for (auto & m_hint : m_hints) {
    const std::string &hint = m_hint.first;

    if (hint.length() < m_curKey.length())
      continue;

    const std::string hintPrefix = hint.substr(0, m_curKey.length());

    if (m_curKey == hintPrefix)
      m_matches[hint] = m_hint.second;
  }
}

/** Show a tooltip with the current relevant hints */
void HintingLineEdit::showToolTip() {
  QString hintList;
  for (auto & m_matche : m_matches) {
    hintList += "<b>" + QString::fromStdString(m_matche.first) + "</b><br />\n";
    if (!m_matche.second.empty())
      hintList += QString::fromStdString(m_matche.second) + "<br />\n";
  }

  if (!hintList.trimmed().isEmpty()) {
    m_hintLabel->show();
    m_hintLabel->setText(hintList.trimmed());
    m_hintLabel->adjustSize();
    m_hintLabel->move(mapToGlobal(QPoint(0, height())));
  } else {
    m_hintLabel->hide();
  }
}

/** Insert an auto completion suggestion beneath the user's cursor and select it
 */
void HintingLineEdit::insertSuggestion() {
  if (m_curKey.length() < 1 || m_matches.size() < 1 || m_dontComplete)
    return;

  // If we don't have a match, just use the first one in the map
  if (m_curMatch.empty())
    m_curMatch = m_matches.begin()->first;

  QString line = text();
  const int curPos = cursorPosition();

  // Don't perform insertions mid-word
  if (curPos + 1 < line.size() && line[curPos + 1].isLetterOrNumber())
    return;

  // Insert a suggestion under the cursor, then select it
  line = line.left(curPos) +
         QString::fromStdString(m_curMatch).mid((int)m_curKey.size()) +
         line.mid(curPos);

  setText(line);
  setSelection(curPos, (int)m_curMatch.size());
}

/** Remove any existing auto completion suggestion */
void HintingLineEdit::clearSuggestion() {
  if (!hasSelectedText())
    return;

  // Carefully cut out the selected text
  QString line = text();
  line = line.left(selectionStart()) +
         line.mid(selectionStart() + selectedText().length());
  setText(line);
}

/** Change to the next available auto completion suggestion */
void HintingLineEdit::nextSuggestion() {
  clearSuggestion();
  // Find the next suggestion in the hint map
  auto it = m_matches.find(m_curMatch);
  if (it != m_matches.end()) {
    it++;
    if (it == m_matches.end())
      m_curMatch = m_matches.begin()->first;
    else
      m_curMatch = it->first;
    insertSuggestion();
  }
}

/** Change to the previous auto completion suggestion */
void HintingLineEdit::prevSuggestion() {
  clearSuggestion();
  // Find the previous suggestion in the hint map
  auto it = m_matches.find(m_curMatch);
  if (it != m_matches.end()) {
    it--;
    if (it == m_matches.end())
      m_curMatch = m_matches.rbegin()->first;
    else
      m_curMatch = it->first;
    insertSuggestion();
  }
}
} // namespace MantidWidgets
} // namepsace MantidQt

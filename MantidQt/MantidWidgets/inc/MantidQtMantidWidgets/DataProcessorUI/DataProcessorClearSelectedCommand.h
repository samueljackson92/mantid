#ifndef MANTIDQTMANTIDWIDGETS_DATAPROCESSORCLEARSELECTEDCOMMAND_H
#define MANTIDQTMANTIDWIDGETS_DATAPROCESSORCLEARSELECTEDCOMMAND_H

#include "MantidQtMantidWidgets/DataProcessorUI/DataProcessorCommandBase.h"

namespace MantidQt {
namespace MantidWidgets {
/** @class DataProcessorClearSelectedCommand

DataProcessorClearSelectedCommand defines the action "Clear Selected"

Copyright &copy; 2011-16 ISIS Rutherford Appleton Laboratory, NScD Oak Ridge
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

File change history is stored at: <https://github.com/mantidproject/mantid>.
Code Documentation is available at: <http://doxygen.mantidproject.org>
*/
class DataProcessorClearSelectedCommand : public DataProcessorCommandBase {
public:
  DataProcessorClearSelectedCommand(DataProcessorPresenter *tablePresenter)
      : DataProcessorCommandBase(tablePresenter){};
  virtual ~DataProcessorClearSelectedCommand(){};

  void execute() override {
    m_presenter->notify(DataProcessorPresenter::ClearSelectedFlag);
  };
  std::string name() override { return std::string("Clear Selected"); }
  std::string icon() override { return std::string("://erase.png"); }
  std::string tooltip() override { return std::string("Clear selected"); }
  std::string whatsthis() override {
    return std::string("Clears the contents of the selected rows");
  }
  std::string shortcut() override { return std::string(); }
};
}
}
#endif /*MANTIDQTMANTIDWIDGETS_DATAPROCESSORCLEARSELECTEDCOMMAND_H*/

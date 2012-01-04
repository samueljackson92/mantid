//----------------------------------------------------------------------
// Includes
//----------------------------------------------------------------------
#include "MantidAPI/WorkspaceGroup.h"
#include "MantidAPI/AnalysisDataService.h"
#include "MantidKernel/Logger.h"
#include "MantidKernel/IPropertyManager.h"

namespace Mantid
{
namespace API
{

Kernel::Logger& WorkspaceGroup::g_log = Kernel::Logger::get("WorkspaceGroup");

WorkspaceGroup::WorkspaceGroup(const bool observeADS) :
  Workspace(), m_deleteObserver(*this, &WorkspaceGroup::workspaceDeleteHandle),
  m_renameObserver(*this, &WorkspaceGroup::workspaceRenameHandle),
  m_wsNames(), m_observingADS(false)
{
  observeADSNotifications(observeADS);
}

WorkspaceGroup::~WorkspaceGroup()
{
  observeADSNotifications(false);
}

/**
 * Turn on/off observing delete and rename notifications to update the group accordingly
 * It can be useful to turn them off when constructing the group.
 * @param observeADS :: If true observe the ADS notifications, otherwise disable them
 */
void WorkspaceGroup::observeADSNotifications(const bool observeADS)
{
  if( observeADS )
  {
    if(!m_observingADS)
    {
      Mantid::API::AnalysisDataService::Instance().notificationCenter.addObserver(m_deleteObserver);
      Mantid::API::AnalysisDataService::Instance().notificationCenter.addObserver(m_renameObserver);
      m_observingADS = true;
    }
  }
  else
  {
    if(m_observingADS)
    {
      Mantid::API::AnalysisDataService::Instance().notificationCenter.removeObserver(m_deleteObserver);
      Mantid::API::AnalysisDataService::Instance().notificationCenter.removeObserver(m_renameObserver);
      m_observingADS = false;
    }
  }
}

/** Add the named workspace to the group
 *  @param name :: The name of the workspace (in the AnalysisDataService) to add
 */
void WorkspaceGroup::add(const std::string& name)
{
  m_wsNames.push_back(name);
  g_log.debug() << "workspacename added to group vector =  " << name <<std::endl;
}

/**
 * Does this group contain the named workspace?
 * @param wsName :: A string to compare
 * @returns True if the name is part of this group, false otherwise
 */
bool WorkspaceGroup::contains(const std::string & wsName) const
{
  std::vector<std::string>::const_iterator itr = std::find(m_wsNames.begin(), m_wsNames.end(), wsName);
  return (itr != m_wsNames.end());
}

/// Empty all the entries out of the workspace group. Does not remove the workspaces from the ADS.
void WorkspaceGroup::removeAll()
{
  m_wsNames.clear();
}

/** Remove the named workspace from the group. Does not delete the workspace from the AnalysisDataService.
 *  @param name :: The name of the workspace to be removed from the group.
 */
void WorkspaceGroup::remove(const std::string& name)
{
  std::vector<std::string>::iterator itr = std::find(m_wsNames.begin(), m_wsNames.end(), name);
  if( itr != m_wsNames.end() )
  {
    m_wsNames.erase(itr);
  }
}

/// Removes all members of the group from the group AND from the AnalysisDataService
void WorkspaceGroup::deepRemoveAll()
{
  if( m_observingADS ) AnalysisDataService::Instance().notificationCenter.removeObserver(m_deleteObserver);
  while (!m_wsNames.empty())
  {
    AnalysisDataService::Instance().remove(m_wsNames.back());
	  m_wsNames.pop_back();
  }
  if( m_observingADS ) AnalysisDataService::Instance().notificationCenter.addObserver(m_deleteObserver);
}

/// Print the names of all the workspaces in this group to the logger (at debug level)
void WorkspaceGroup::print() const
{
  std::vector<std::string>::const_iterator itr;
  for (itr = m_wsNames.begin(); itr != m_wsNames.end(); ++itr)
  {
    g_log.debug() << "Workspace name in group vector =  " << *itr << std::endl;
  }
}

/**
 * Callback for a workspace delete notification
 * @param notice :: A pointer to a workspace delete notificiation object
 */
void WorkspaceGroup::workspaceDeleteHandle(Mantid::API::WorkspacePostDeleteNotification_ptr notice)
{
  const std::string deletedName = notice->object_name();
  if( !this->contains(deletedName)) return;

  if( deletedName != this->getName() )
  {
    this->remove(deletedName);
    if(isEmpty())
    {
     Mantid::API::AnalysisDataService::Instance().remove(this->getName());
    }
  }
}

/**
 * Callback for a workspace rename notification
 * @param notice :: A pointer to a workspace rename notfication object
 */
void WorkspaceGroup::workspaceRenameHandle(Mantid::API::WorkspaceRenameNotification_ptr notice)
{
  std::vector<std::string>::iterator itr = 
    std::find(m_wsNames.begin(), m_wsNames.end(), notice->object_name());
  if( itr != m_wsNames.end() )
  {
    (*itr) = notice->new_objectname();
  }
}

/**
 * This method returns true if the workspace group is empty
 * @return true if workspace is empty
 */
bool WorkspaceGroup::isEmpty() const
{
	return m_wsNames.empty();
}

} // namespace API
} // namespace Mantid

/// @cond TEMPLATE

namespace Mantid
{
  namespace Kernel
  {

    template<> MANTID_API_DLL
      Mantid::API::WorkspaceGroup_sptr IPropertyManager::getValue<Mantid::API::WorkspaceGroup_sptr>(const std::string &name) const
    {
      PropertyWithValue<Mantid::API::WorkspaceGroup_sptr>* prop =
        dynamic_cast<PropertyWithValue<Mantid::API::WorkspaceGroup_sptr>*>(getPointerToProperty(name));
      if (prop)
      {
        return *prop;
      }
      else
      {
        std::string message = "Attempt to assign property "+ name +" to incorrect type. Expected WorkspaceGroup.";
        throw std::runtime_error(message);
      }
    }

    template<> MANTID_API_DLL
      Mantid::API::WorkspaceGroup_const_sptr IPropertyManager::getValue<Mantid::API::WorkspaceGroup_const_sptr>(const std::string &name) const
    {
      PropertyWithValue<Mantid::API::WorkspaceGroup_sptr>* prop =
        dynamic_cast<PropertyWithValue<Mantid::API::WorkspaceGroup_sptr>*>(getPointerToProperty(name));
      if (prop)
      {
        return prop->operator()();
      }
      else
      {
        std::string message = "Attempt to assign property "+ name +" to incorrect type. Expected const WorkspaceGroup.";
        throw std::runtime_error(message);
      }
    }

  } // namespace Kernel
} // namespace Mantid

/// @endcond TEMPLATE


// from mantid
#include "MantidScriptRepository/ScriptRepositoryImpl.h"
#include "MantidAPI/ScriptRepositoryFactory.h"
#include "MantidKernel/Logger.h"
#include "MantidKernel/ConfigService.h"
#include <utility>
using Mantid::Kernel::Logger;
using Mantid::Kernel::ConfigService;
using Mantid::Kernel::ConfigServiceImpl; 

// from poco
#include <Poco/Path.h>
#include <Poco/File.h>
#include <Poco/TemporaryFile.h>
#include <Poco/URI.h>
#include <Poco/Net/HTTPClientSession.h>
#include <Poco/Net/HTTPRequest.h>
#include <Poco/Exception.h>
#include <Poco/Net/HTTPResponse.h>
#include <Poco/Net/NetException.h>
#include <Poco/Net/HTMLForm.h>
#include "Poco/Net/FilePartSource.h"


// Visual Studion compains with the inclusion of Poco/FileStream
// disabling this warning.
#if defined(_WIN32) || defined(_WIN64)
#pragma warning( push )
#pragma warning( disable : 4250 )
#include <Poco/FileStream.h>
#include <Poco/NullStream.h>
#pragma warning( pop )
#else
#include <Poco/FileStream.h>
#include <Poco/NullStream.h>
#endif
#include <Poco/StreamCopier.h>
#include <Poco/Net/NetException.h>
#include <Poco/DirectoryIterator.h>
#include <Poco/DateTimeParser.h>
#include <Poco/DateTimeFormatter.h>

// from boost
#include <boost/property_tree/ptree.hpp>
#include <boost/property_tree/json_parser.hpp>
#include <boost/foreach.hpp>
#include <boost/algorithm/string.hpp> 
#include <boost/regex.hpp>

using boost::property_tree::ptree;

namespace Mantid
{
namespace API
{

  static void notImplemented(){
    throw ScriptRepoException("This method is not implemented yet"); 
  };
  
  static ScriptRepoException pocoException(const std::string & info, 
                                           Poco::Exception & ex){
    std::stringstream ss;     
    if (dynamic_cast<Poco::FileAccessDeniedException*>(&ex))
      ss << info << ", because you do not have access to write to this path :"<< ex.message() << std::ends;     
    else if (dynamic_cast<Poco::Net::HostNotFoundException*>(&ex))
      ss << info << ". The definition of the remote url is not correct. Please check the Mantid settings, the ScriptRepository entry. Current: " << ex.message() << std::ends;
    else{
      ss << info << " . Unkown:" << ex.displayText() <<std::ends; 
    }
      
    return ScriptRepoException(ss.str(), ex.displayText()); 
  }

  const char * timeformat = "%Y-%b-%d %H:%M:%S"; 

  const char * emptyURL = "The initialization failed because no URL was given that points "
    "to the central repository.\nThis entry should be defined at the properties file, "
    "at ScriptRepository";


  DECLARE_SCRIPTREPOSITORY(ScriptRepositoryImpl)
  /**
     The main information that ScriptrepositoryImpl needs to be able 
     to operate are where the local repository is (or will be), and
     the url for the mantid web server. 
     
     Usually these values are available at the Mantid properties files, 
     so, it is possible to construct the ScriptrepositoryImpl without
     parameters.
     
     But, for flexibility reasons, (for example, testing with other
     repositories), a more general constructor is provided. 
     
     In case a string is passed to the constructor different from the 
     default one, it will have precedence, but it will not override what
     is defined by the Mantid properties files. These values will be valid
     only for that instance. 
     
     Currently, two properties are defined: ScriptLocalRepository, and ScriptRepository. 
     
     @code
     // get ScriptRepository and ScriptLocalRepository values from Mantid Config Service
     ScriptrepositoryImpl sharing(); 
     // apply given values
     ScriptrepositoryImpl sharing("/tmp/gitrep", 
     "http://repository.mantidproject.com");      
     @endcode
  */
  ScriptRepositoryImpl::ScriptRepositoryImpl(const std::string & local_rep, 
                                         const std::string & remote) :
  g_log(Logger::get("ScriptRepositoryImpl"))
  {    
    // get the local path and the remote path
    std::string loc, rem; 
    ConfigServiceImpl & config = ConfigService::Instance();
    remote_upload = config.getString("UploaderWebServer"); 
    if (local_rep.empty() || remote.empty()){
      loc = config.getString("ScriptLocalRepository"); 
      rem = config.getString("ScriptRepository");      
    }else{
      local_repository = local_rep; 
      remote_url = remote; 
    }
    // the parameters given from the constructor have precedence
    if (local_rep.empty())
      local_repository = loc; 
    else
      local_repository = local_rep; 
    
    if (local_repository[local_repository.size()-1] != '/')
      local_repository.append("/");

    if (remote.empty())
      remote_url = rem; 
    else
      remote_url = remote;


    // empty remote url is not allowed
    if (remote_url.empty()){
      g_log.error() << emptyURL<<std::endl; 
      throw ScriptRepoException(emptyURL,"Constructor Failed: remote_url.empty");
    }

    if (remote_url[remote_url.size()-1] != '/')
      remote_url.append("/");


    g_log.debug() << "ScriptRepository creation pointing to " 
                  << local_repository << " and " << remote_url << "\n";


    
    // check if the repository is valid.
    valid = false;
    // if no folder is given, the repository is invalid.
    if (local_repository.empty())
      return;

    // parsing the ignore pattern
    std::string ignore = ignorePatterns(); 
    boost::replace_all(ignore,"/","\\/");
    boost::replace_all(ignore,";","|");
    boost::replace_all(ignore,".","\\.");
    boost::replace_all(ignore,"*",".*");
    ignoreregex = std::string("(").append(ignore).append(")");  


    // A valid repository must pass 3 tests:
    //  - An existing folder
    //  - This folder must have the .repository.json file
    //  - This folder must have the .local.json file
    // These tests will be done with Poco library

      
    Poco::Path local(local_repository); 
    
    std::string aux_local_rep;
    if (local.isRelative()){
      aux_local_rep = std::string(Poco::Path::current()).append(local_repository);
      local_repository = aux_local_rep;
    }

    
    try{// tests 1 and 2
      {
        Poco::File local_rep_dir(local);
        std::string repository_json = std::string(local_repository).append(".repository.json");
        Poco::File rep_json(repository_json);
        if (!local_rep_dir.exists() || !rep_json.exists()){
          g_log.information() << "ScriptRepository was not installed at " << local_repository << std::endl; 
          return; // this is an invalid repository, because it was not created (installed)
        }
      }
      // third test
      {
        std::string repository_json = std::string(local_repository).append(".local.json");
        Poco::File rep_json(repository_json);      
        if (!rep_json.exists()){
          g_log.error() << "Corrupted ScriptRepository at "<< local_repository 
                        << ". Please, remove this folder, and install ScriptRepository again" 
                        << std::endl;
          
        }
      }
    }catch(Poco::FileNotFoundException & /*ex*/){
      g_log.error() << "Testing the existence of repository.json and local.json failed"<<std::endl; 
      return;
    }

    // this is necessary because in windows, the absolute path is given with \ slash.
    boost::replace_all(local_repository,"\\","/");
    if (local_repository[local_repository.size()-1] != '/')
      local_repository.append("/");

    repo.clear();
    valid = true;
  }


  ScriptRepositoryImpl::~ScriptRepositoryImpl() throw() {

  }


  /**
     Check the connection with the server through the ::doDownloadFile method.
     @path server : The url that will be used to connect.
   */
  void ScriptRepositoryImpl::connect(const std::string & server){
    doDownloadFile(server);
  }

  /** Implements the ScriptRepository::install method. 
      
      The instalation consists of: 
      
        - creation of the folder for the ScriptRepository (if it does not exists).
        - download of the repository.json file (Make it hidden)
        - creation of the local.json file. (Make if hidden)
        
      The installation will also upate the ScriptLocalRepository setting, if necessary,
      to match the given path. 
        
      If it success, it will change the status of the ScriptRepository as valid.
      
      @note Any directory may be given, from existing directories a new directory. 
      If an existing directory is given, the installation will install the two necessary 
      files to deal with this folder as a ScriptRepository.
      

      @param path : Path for a folder inside the local machine.
      
      
   */
  void ScriptRepositoryImpl::install(const std::string &  path){
    using Poco::DirectoryIterator;
    std::string folder = std::string(path); 
    Poco::File repository_folder(folder); 
    std::string rep_json_file = std::string(path).append("/.repository.json");
    std::string local_json_file  = std::string(path).append("/.local.json");
    if (!repository_folder.exists()){
      repository_folder.createDirectories();
    }
      
    // install the two files inside the given folder
    
    // download the repository json
    doDownloadFile(std::string(remote_url).append("repository.json"),
                   rep_json_file);
    g_log.debug() << "ScriptRepository downloaded repository information" << std::endl; 
    // creation of the instance of local_json file
    Poco::File local(local_json_file); 
    if (!local.exists()){
      ptree pt; 
      write_json(local_json_file,pt); 
      g_log.debug() << "ScriptRepository created the local repository information"
                    <<std::endl; 
    }
    
    #if defined(_WIN32) ||  defined(_WIN64)
    //set the .repository.json and .local.json hidden
    SetFileAttributes( local_json_file.c_str(), FILE_ATTRIBUTE_HIDDEN); 
    SetFileAttributes (rep_json_file.c_str(), FILE_ATTRIBUTE_HIDDEN);
    #endif
    
    // save the path to the config service
    //
    ConfigServiceImpl & config = ConfigService::Instance();
    std::string loc = config.getString("ScriptLocalRepository"); 
    if (loc != path){
      config.setString("ScriptLocalRepository", path); 
      config.saveConfig(config.getUserFilename()); 
    }

    local_repository = path;
    // this is necessary because in windows, the absolute path is given with \ slash.
    boost::replace_all(local_repository,"\\","/");
    if (local_repository[local_repository.size()-1] != '/')
      local_repository.append("/");

    valid = true;
  }

  void ScriptRepositoryImpl::ensureValidRepository(){
    if (!isValid()){
      std::stringstream ss; 
      ss << "ScriptRepository is not installed correctly. The current path for ScriptRepository is " 
         << local_repository << " but some important files that are required are corrupted or not present."
         << "\nPlease, re-install the ScriptRepository!\n"
         << "Hint: if you have a proper installation in other path, check the property ScriptLocalRepository "
         << "at the Mantid.user.properties and correct it if necessary."; 
      throw ScriptRepoException(ss.str(),"CORRUPTED"); 
    }
  }

  /** Implements ScriptRepository::info

      For each entry inside the repository, there are some usefull information, that are stored in 
      a ::ScriptInfo struct. 
      
      Use this method, to get information about the description, last modified date, the auto update
      flag and the author. 
      
      @param input_path: The path (relative or absolute) to the file/folder entry,
      
      @return ScriptInfo with the information of this file/folder.

      @note: This method requires that ::listFiles was executed at least once.

  */
  ScriptInfo ScriptRepositoryImpl::info(const std::string & input_path) {
    ensureValidRepository();
    std::string path = convertPath(input_path);
    ScriptInfo info; 
    try{
      RepositoryEntry & entry = repo.at(path); 
      info.author = entry.author; 
      info.pub_date = entry.pub_date;
      info.auto_update = entry.auto_update;
      info.directory = entry.directory; 
    }catch(const std::out_of_range & ex){
      std::stringstream ss; 
      ss << "The file \""<< input_path << "\" was not found inside the repository!";            
      throw ScriptRepoException(ss.str(), ex.what()); 
    }
    return info; 
  }

 const std::string& ScriptRepositoryImpl::description(const std::string & input_path){
    ensureValidRepository();
    std::string path = convertPath(input_path);
    try{
      RepositoryEntry & entry = repo.at(path); 
      return entry.description; 
    }catch(const std::out_of_range & ex){
      std::stringstream ss; 
      ss << "The file \""<< input_path << "\" was not found inside the repository!";            
      throw ScriptRepoException(ss.str(), ex.what()); 
    }
  }

  /** 
      Implement the ScriptRepository::listFiles. 
      
      It will fill up the ScriptRepositoryImpl::Repository variable in order to provide
      information about the status of the file as well.
      
      In order to list all the values from the repository, it uses three methods:

       - ::parseCentralRepository
       - ::parseDonwloadedEntries
       - ::parseLocalRepository

      After this, it will perform a reverse iteration on all the entries of the repository
      in order to evaluate the status (::findStatus) of every file, and will also get the 
      status of every directory, by accumulating the influency of every directory. 
      
      The listFiles will list:
        - all files in the central repository
        - all files in the local repository

      @return It returns a list of all the files and directories (the relative path inside the repository).
  */
  std::vector<std::string> ScriptRepositoryImpl::listFiles() {
    ensureValidRepository();
    
    repo.clear();
    assert(repo.size() == 0);
    try{
      parseCentralRepository(repo); 
      parseLocalRepository(repo);
      parseDownloadedEntries(repo);
      // it will not catch ScriptRepositoryExc, because, this means, that it was already processed.
      // it will proceed in this situation.
    }catch(Poco::Exception & ex){
      g_log.error() << "ScriptRepository failed to list all entries inside the repository. Details: " << ex.className() << ":> " << ex.displayText() << std::endl;       
    }catch(std::exception & ex){
      g_log.error() << "ScriptRepository failed to list all entries inside the repository. Details: " << ex.what() << std::endl; 
    }
    std::vector<std::string> out(repo.size());
    size_t i = repo.size(); 

    // evaluate the status for all entries
    // and also fill up the output vector (in reverse order)
    Mantid::API::SCRIPTSTATUS acc_status = Mantid::API::BOTH_UNCHANGED;
    std::string last_directory = ""; 
    for (Repository::reverse_iterator it = repo.rbegin();
         it != repo.rend();
           it++){
      // for every entry, it takes the path and RepositoryEntry
      std::string entry_path = it->first; 
      RepositoryEntry & entry = it->second;
      //g_log.debug() << "Evaluating the status of " << entry_path << std::endl;
      // fill up the output vector
      out[--i] = it->first;
      //g_log.debug() << "inserting file: " << it->first << std::endl; 

      // for the directories, update the status of this directory
      if (entry.directory){
        entry.status = acc_status; 
        last_directory = entry_path;        
      }else{
        // for the files, it evaluates the status of this file
        
        if (entry.local && !entry.remote){
          // entry local only
          entry.status = LOCAL_ONLY;         
        }else if (!entry.local && entry.remote){
          // entry remote only
          entry.status = REMOTE_ONLY;
        }else{
          // there is no way of not being remote nor local!
          
          // entry is local and is remote
          // the following status are available: 
          // BOTH_CHANGED, BOTH_UNCHANGED, REMOTE_CHANGED, LOCAL_CHANGED.
          enum CHANGES{UNCH=0,REMO=0X1,LOC=0X2, BOTH=0X3};
          int st = UNCH; 
          // the file is local_changed, if the date of the current file is diferent
          // from the downloaded one.
          if (entry.current_date != entry.downloaded_date)
            st |= LOC; 
          // the file is remote_changed if the date of the pub_date file is 
          // diferent from the local downloaded pubdate.
          if (entry.pub_date != entry.downloaded_pubdate)
            st |= REMO; 
          
          

          switch(st){
          case UNCH:
            entry.status = BOTH_UNCHANGED; 
            break;
          case REMO:
            entry.status = REMOTE_CHANGED;
            break;
          case LOC:
            entry.status = LOCAL_CHANGED;
            break;
          case BOTH:
          default:
            entry.status = BOTH_CHANGED;
            break;            
          }// end switch

        }// end evaluating the file status      

      }// end dealing with files
      
      // is this entry a child of the last directory?
      if (!last_directory.empty()){
        if (entry_path.find(last_directory) == std::string::npos){
          // no, this entry is not a child of the last directory
          // restart the status
          acc_status = Mantid::API::BOTH_UNCHANGED;
        }
      }
      
      // update the status of the parent directory:
      // the strategy here is to compare binary the current status with the acc_state
      switch(acc_status | entry.status){
        // pure matching, meaning that the matching is done with the same state
        // or with BOTH_UNCHANGED (neutral)
      case BOTH_UNCHANGED: // BOTH_UNCHANGED IS 0, so only 0|0 match this option
      case REMOTE_ONLY: // REMOTE_ONLY IS 0x01, so only 0|0x01 and 0x01|0x01 match this option
      case LOCAL_ONLY:  
      case LOCAL_CHANGED:
      case REMOTE_CHANGED:
        acc_status = (SCRIPTSTATUS)(acc_status | entry.status);
        break;
      case LOCAL_ONLY | LOCAL_CHANGED:
        acc_status = LOCAL_CHANGED;
      case REMOTE_ONLY | REMOTE_CHANGED:
        acc_status = REMOTE_CHANGED;
      default:
        acc_status = BOTH_CHANGED;
        break;        
      }     
      
    }

    return out;
  } 

  /**
     Implements the ScriptRepository::download. 

     @note Require that ::listFiles been called at least once. 
     
     The download is able to download files or directories. Internally, 
     it will assign the job to the ::download_diretory or ::download_file. 
     
     This method, just ensure that the entry is valid (wich means,
     it is inside the repository). 
     
     @param input_path: The path for the file/folder to be downloaded.

     @note As a result of the download a new file, the local repository 
     information .local.repository will be changed.
     
  */

  void ScriptRepositoryImpl::download(const std::string & input_path){
    ensureValidRepository();
    std::string file_path = convertPath(input_path);
    try{
      RepositoryEntry & entry = repo.at(file_path); 
      if (entry.directory)
        download_directory(file_path);
      else
        download_file(file_path, entry);
    }catch(const std::out_of_range & ex){
      // fixme: readable exception
      throw ScriptRepoException(ex.what()); 
    }

  }


  /**
     Go recursively to download all the children of an input directory. 
     
     @param directory_path : the path for the directory.
   */
  void ScriptRepositoryImpl::download_directory(const std::string & directory_path){
    std::string directory_path_with_slash = std::string(directory_path).append("/");
    bool found = false; 
    for(Repository::iterator it = repo.begin();
        it != repo.end(); it++){
      // skip all entries that are not children of directory_path
      // the map will list the entries in alphabetical order, so, 
      // when it first find the directory, it will list all the 
      // childrens of this directory, and them, 
      // it will list other things, so we can, break the loop
      if (it->first.find(directory_path) != 0){
        if (found) 
          break; // for the sake of performance
        else
          continue;
      }
      found = true;
      if (it->first != directory_path &&
          it->first.find(directory_path_with_slash) != 0)
        {
          // it is not a children of this entry, just similar. Example: 
          // TofConverter/README
          // TofConverter.py
          // these two pass the first test, but will not pass this one.
          found = false;
          continue; 
        }
      // now, we are dealing with the children of directory path
      if (!it->second.directory)
        download_file(it->first, it->second);
      else{
        // download the directory. 

        // we will not download the directory, but create one with the
        // same name, and update the local json
        
        Poco::File dir(std::string(local_repository).append(it->first));
        dir.createDirectories();
        
        it->second.status = BOTH_UNCHANGED;         
        it->second.downloaded_date = DateAndTime(
             Poco::DateTimeFormatter::format(dir.getLastModified(),
                                             timeformat));
        it->second.downloaded_pubdate = it->second.pub_date;
        updateLocalJson(it->first, it->second);
      
      }// end donwloading directory
      // update the status
      it->second.status = BOTH_UNCHANGED; // update this entry
    }// end interaction with all entries

  }


  /**
     Download the real file from the remote_url.
     
     @todo describe better this method.
   */
  void ScriptRepositoryImpl::download_file(const std::string &file_path, RepositoryEntry & entry) {
    SCRIPTSTATUS state = entry.status;
    // if we have the state, this means that the entry is available
    if (state == LOCAL_ONLY  || state == LOCAL_CHANGED){
      std::stringstream ss; 
      ss << "The file " << file_path << " can not be download because it has only local changes."
         << " If you want, please, publish this file uploading it" ; 
      throw ScriptRepoException(ss.str()); 
    }
    
    if (state == BOTH_UNCHANGED)
      // instead of throwing exception, silently assumes that the download was done.
      return;
           
    // download the file
    std::string url_path = std::string(remote_url).append(file_path); 
    Poco::TemporaryFile tmpFile; 
    doDownloadFile(url_path, tmpFile.path());

    std::string local_path = std::string(local_repository).append(file_path); 
    g_log.debug() << "ScriptRepository download url_path: " << url_path << " to " << local_path << std::endl;


    try{

      if (state == BOTH_CHANGED){
        // make a back up of the local version
        Poco::File f(std::string(local_repository).append(file_path));
        std::string bck = std::string(f.path()).append("_bck");
        g_log.notice() << "The current file " << f.path() << " has some local changes"
                       << " so, a back up copy will be created at " << bck << std::endl; 
        f.copyTo(bck);         
      }
      
      // ensure that the path to the local_path exists    
      size_t slash_pos = local_path.rfind('/');
      Poco::File file_out(local_path);
      if (slash_pos != std::string::npos){
        std::string dir_path = std::string(local_path.begin(),local_path.begin()+slash_pos);
        if (!dir_path.empty()){
          Poco::File dir_parent(dir_path);
          if (!dir_parent.exists()){
            dir_parent.createDirectories();
          }
        }// dir path is empty
      }
      
      if (!file_out.exists())
        file_out.createFile();

      tmpFile.copyTo(local_path); 
      
    }catch(Poco::FileAccessDeniedException & ex){
      std::stringstream ss; 
      ss << "You cannot create file at " << local_path << ". Not downloading ..."; 
      throw ScriptRepoException(ss.str());      
    }

    {
      Poco::File local(local_path);
      entry.downloaded_date = DateAndTime(Poco::DateTimeFormatter::format(local.getLastModified(),
                                                                          timeformat));
      entry.downloaded_pubdate = entry.pub_date;
      entry.status = BOTH_UNCHANGED;      
    }
    
    updateLocalJson(file_path, entry); ///FIXME: performance!    
    g_log.debug() << "ScriptRepository download " << local_path << " success!"<<std::endl; 
  }

  /**
    @todo Describe
  */
  SCRIPTSTATUS ScriptRepositoryImpl::fileStatus(const std::string & input_path) {
    /// @todo: implement the trigger method to know it we need to revised the 
    ///        directories trees.    
    ensureValidRepository();
    std::string file_path = convertPath(input_path); 
    //g_log.debug() << "Attempt to ask for the status of "<< file_path << std::endl;
    try{
      RepositoryEntry & entry = repo.at(file_path); 
      return entry.status;
    }catch(const std::out_of_range & ex){
      std::stringstream ss; 
      ss << "The file \""<< input_path << "\" was not found inside the repository!";            
      throw ScriptRepoException(ss.str(), ex.what()); 
    }
    // this line will never be executed, just for avoid compiler warnings.
    return BOTH_UNCHANGED;
  }

  /**
   * Uploads one file to the ScriptRepository web server, pushing, indirectly, to the 
   * git repository. It will send in a POST method, the file and the following fields: 
   *  - author : Will identify the author of the change
   *  - email:  Will identify the email of the author
   *  - comment: Description of the nature of the file or of the update
   *  
   * It will them upload to the URL pointed to UploaderWebServer. It will them receive a json file 
   * with some usefull information about the success or failure of the attempt to upload. 
   * In failure, it will be converted to an appropriated ScriptRepoException.
  */
  void ScriptRepositoryImpl::upload(const std::string & file_path, 
                                    const std::string & comment,
                                    const std::string & author, 
                                    const std::string & email)
    
  {
    using namespace Poco::Net;
    try{
      Poco::URI uri(remote_upload); 
      std::string path(uri.getPathAndQuery());
      HTTPClientSession session(uri.getHost(), uri.getPort()); 
      HTTPRequest req(HTTPRequest::HTTP_POST, path, 
                      HTTPMessage::HTTP_1_0); 
      HTMLForm form(HTMLForm::ENCODING_MULTIPART); 
      
      // add the fields author, email and comment
      form.add("author",author); 
      form.add("mail", email); 
      form.add("comment",comment); 
      
      // deal with the folder
      std::string relative_path = convertPath(file_path); 
      std::string absolute_path = local_repository + relative_path; 
      std::string folder = "./"; 
      size_t pos = relative_path.rfind('/'); 
      if (pos != std::string::npos)
        folder += std::string(relative_path.begin(), relative_path.begin() + pos);
      if (folder[folder.size()-1] != '/')
        folder += "/";
      g_log.information() << "Uploading to folder: " << folder << std::endl; 
      form.add("path",folder); 
      
      // inserting the file
      FilePartSource * m_file = new FilePartSource(absolute_path);
      form.addPart("file",m_file); 
      form.prepareSubmit(req);
      
      // get the size of everything
      std::stringstream sst; 
      form.write(sst); 
      // move back to the begining of the file
      m_file->stream().clear();
      m_file->stream().seekg(0,std::ios::beg);  
      // set the size
      req.setContentLength((int)sst.str().size());
      
      std::ostream& ostr = session.sendRequest(req);
      // send the request.
      ostr << sst.str(); 
      
      HTTPResponse response;
      std::istream & rs = session.receiveResponse(response);
      
      if (response.getStatus() == HTTPResponse::HTTP_OK){
      g_log.information() << "ScriptRepository:" << file_path <<  " uploaded!"<< std::endl; 
      }else{
        // FIXME: deal with exceptions.
        g_log.information() << "ScriptRepository upload status: " 
                            << response.getStatus() << " " << response.getReason() << std::endl;
        std::stringstream answer; 
        Poco::StreamCopier::copyStream(rs, answer);
        g_log.debug() << "Form Output: " << answer.str() << std::endl; 
        
        ptree pt; 
        try{
          read_json(answer, pt); 
          std::string info = pt.get<std::string>("message",""); 
          std::string detail = pt.get<std::string>("detail","");
          std::string cmd = pt.get<std::string>("shell",""); 
          if (!cmd.isEmpty())
            detail.append("\nFrom Command: ").append(cmd)
          throw ScriptRepoException(info, detail); 
          
        }catch (boost::property_tree::json_parser_error & ex){
          throw ScriptRepoException("Bad answer from the Server",
                                    ex.what()); 
        }
      }
    }catch(Poco::Exception & ex){
      throw ScriptRepoException(ex.displayText(), ex.className()); 
    }
  }

  /** The ScriptRepositoryImpl is set to be valid when the local repository path
      points to a valid folder that has also the .repository.json and .local.json files. 
      
      An invalid repository accepts only the ::install method. 
   */
  bool ScriptRepositoryImpl::isValid(void){
    return valid;
  }

  /** 
      @todo describe
  */
  void ScriptRepositoryImpl::check4Update(void) 
  {
    g_log.debug() << "ScriptRepositoryImpl checking for update\n" ; 
    // download the new repository json file
    // download the repository json
    std::string rep_json_file = std::string(local_repository).append(".repository.json");
    std::string backup = std::string(rep_json_file).append("_backup");
    { 
      Poco::File f(rep_json_file);
      f.moveTo(backup); 
    }
    try{
      doDownloadFile(std::string(remote_url).append("repository.json"),
                   rep_json_file);
    }catch(...){
      // restore file
      Poco::File f(backup); 
      f.moveTo(rep_json_file);
      throw;
    }
    
    // remote backup
    {
      Poco::File bak(backup);
      bak.remove(); 
    }

    #if defined(_WIN32) ||  defined(_WIN64)
    //set the .repository.json and .local.json hidden
    SetFileAttributes (rep_json_file.c_str(), FILE_ATTRIBUTE_HIDDEN);
    #endif

    // re list the files
    listFiles(); 
    
    // look for all the files in the list, to check those that 
    // has the auto_update and check it they have changed.
    for(Repository::iterator it = repo.begin(); 
        it!= repo.end();
        it++){
      if (it->second.auto_update){
        // THE SAME AS it->status in (REMOTE_CHANGED, BOTH_CHANGED)
        if (it->second.status & REMOTE_CHANGED){
          download(it->first); 
        }
      }
    }
    g_log.debug() << "ScriptRepositoryImpl::checking for update finished\n" ; 
  }

  /** 
      @todo describe
  */
  void ScriptRepositoryImpl::setIgnorePatterns(const std::string & patterns){
    ConfigServiceImpl & config = ConfigService::Instance();
    std::string ignore = config.getString("ScriptRepositoryIgnore"); 
    if (ignore != patterns){
      config.setString("ScriptRepositoryIgnore", patterns); 
      config.saveConfig(config.getUserFilename()); 
      std::string newignore=patterns; 
      boost::replace_all(ignore,"/","\\/");
      boost::replace_all(newignore,";","|");      
      boost::replace_all(newignore,".","\\.");
      boost::replace_all(newignore,"*",".*");      
      ignoreregex = std::string("(").append(newignore).append(")");
    }
  };
  /** 
      @todo describe
  */
  std::string ScriptRepositoryImpl::ignorePatterns(void){    
    ConfigServiceImpl & config = ConfigService::Instance();
    std::string ignore_string = config.getString("ScriptRepositoryIgnore",""); 
    return ignore_string;
  }

  /** 
      @todo describe
  */
  void ScriptRepositoryImpl::setAutoUpdate(const std::string & input_path, bool option){
    ensureValidRepository();
    std::string path = convertPath(input_path); 
    //g_log.debug() << "SetAutoUpdate... begin" << std::endl; 
    try{
      RepositoryEntry & entry = repo.at(path);
      entry.auto_update = option; 
      updateLocalJson(path,entry); 
    }catch(const std::out_of_range & ex){
      // fixme: readable exception
      throw ScriptRepoException(ex.what()); 
    }
    //g_log.debug() << "SetAutoUpdate... end" << std::endl; 
  }
  

/** Download a url and fetch it inside the local path given.
      
      Provide a clear separation between the logic behind the ScriptRepositoryImpl and 
      the Mantid Web Service. This is the only method for the downloading and update
      that performs a real connection to the Mantid Web Service. 
      
      This method was presente at the Script Repository Design, as an strategy to perform 
      unit tests, but also, helps the definition of a clear separation of the logic and 
      organization of the ScriptRepository, from the conneciton to the Mantid Web service, 
      making it more decoupled. 
      
      @param url_file: Define a valid URL for the file to be downloaded. Eventually, it may give
      any valid http path. For example: 
      
      url_file = "http://www.google.com" 
      
      url_file = "http://mantidweb/repository/README.md"
      
      The result it to connect to the http server, and request the path given.
      
      The answer, will be inserted at the local_file_path. 
      
      @param local_file_path [optional] : Provide the destination of the file downloaded at the url_file. 
      If an empty string is provided (default value), it will discard the result, but it will ensure that
      the connection and the download was done correctly.
      
      @exception ScriptRepoException: For any unexpected behavior.      
  */
  void ScriptRepositoryImpl::doDownloadFile(const std::string & url_file, 
                                            const std::string & local_file_path)
  {
    // get the information from url_file
    Poco::URI uri(url_file);
    std::string path(uri.getPathAndQuery());
    if (path.empty()) path = "/";
    std::string given_path = std::string(path.begin()+18, path.end());// remove the "/scriptrepository/" from the path
    //Configure Poco HTTP Client Session
    try{
      Poco::Net::HTTPClientSession session(uri.getHost(), uri.getPort());
      session.setTimeout(Poco::Timespan(2,0));// 2 secconds
      Poco::Net::HTTPRequest request(Poco::Net::HTTPRequest::HTTP_GET, path,
                                     Poco::Net::HTTPMessage::HTTP_1_1);
      Poco::Net::HTTPResponse response;

      session.sendRequest(request); 

      std::istream & rs = session.receiveResponse(response); 
      g_log.debug() << "Answer from mantid web: " << response.getStatus() << " " 
                    << response.getReason() << std::endl; 
      if (response.getStatus() == Poco::Net::HTTPResponse::HTTP_OK ){
        if (local_file_path.empty()){
          // ignore the answer, trow it away
          Poco::NullOutputStream null; 
          Poco::StreamCopier::copyStream(rs,null); 
          return;
        }else{
          // copy the file
          Poco::FileStream _out(local_file_path); 
          Poco::StreamCopier::copyStream(rs,_out); 
          _out.close();           
        }
      }else{
        std::stringstream info;
        std::stringstream ss;
        Poco::StreamCopier::copyStream(rs,ss);        
        if (response.getStatus() == Poco::Net::HTTPResponse::HTTP_NOT_FOUND)
          info << "Failed to download " << given_path 
               << " because it failed to find this file at the link " 
               << "<a href=\""
               << url_file << "\">.\n"
               << "Hint. Check that link is correct and points to the correct server "
               << "which you can find at <a href=\"http://www.mantidproject.org/ScriptRepository\">"
               << "Script Repository Help Page</a>"; 
        else{          
          // show the error
          // fixme, process this error          
          info << response.getReason();
          info << ss.str();
        }
        throw ScriptRepoException(info.str(), ss.str()); 
      }
    }catch(Poco::Net::HostNotFoundException & ex){
      // this exception occurrs when the pc is not connected to the internet
      std::stringstream info; 
      info <<  "Failed to download " << given_path << " because there is no connection to the host "
           << ex.message() << ".\nHint: Check your connection following this link: <a href=\""
           << url_file << "\">" << given_path << "</a>";
      throw ScriptRepoException(info.str(), ex.displayText(), __FILE__, __LINE__);
    
    }catch (Poco::Exception & ex){
      throw pocoException("Connection and request failed", ex);
    }
  }

  /** 
      @todo describe
  */
  void ScriptRepositoryImpl::parseCentralRepository(Repository & repo){    
    ptree pt; 
    std::string filename = std::string(local_repository).append(".repository.json");
    try{
      read_json(filename, pt);
      
      BOOST_FOREACH(ptree::value_type & file, pt){
        if (!isEntryValid(file.first))
          continue;
        //g_log.debug() << "Inserting : file.first " << file.first << std::endl;
        RepositoryEntry & entry = repo[file.first];
        entry.remote = true;
        entry.directory = file.second.get("directory",false);
        entry.pub_date = DateAndTime(file.second.get<std::string>("pub_date"));
        entry.description = file.second.get("description",""); 
        entry.author = file.second.get("author",""); 
        entry.status = BOTH_UNCHANGED;
      }
      
    }catch (boost::property_tree::json_parser_error & ex){
      std::stringstream ss;
      ss << "Corrupted database : " << filename; 
      
      g_log.error() << "ScriptRepository: " << ss.str() 
                    << "\nDetails: json_parser_error: " << ex.what() << std::endl; 
      throw ScriptRepoException(ss.str(), ex.what()); 
    }catch(std::exception & ex){
      std::stringstream ss; 
      ss << "RuntimeError: checking database >> " << ex.what();
      g_log.error() << "ScriptRepository: " << ss.str() << ". Input: " << filename << std::endl;
      throw ScriptRepoException(ss.str(), filename); 
    }catch(...){
      g_log.error() << "FATAL Unknown error (checking database): " << filename << std::endl;
      throw;
    }
  }
    /** 
      @todo describe
  */
  void ScriptRepositoryImpl::parseLocalRepository(Repository & repo){
    recursiveParsingDirectories(local_repository, repo); 
  }
  /** 
      This method will parse through all the entries inside the local.json 
      file to get the information about the downloaded date and the version 
      of the downloaded file. This information will be used to extract the 
      status of the file entry. 

      All the entries should be already created before, because, if the entry 
      was once downloaded, it should be already at the central repository, 
      as well as in the local file system.

      The parseDownloadedEntries is not expected to create any new entry.
      If it finds that the entry is not set as local.
      
      The parseDownloadedEntries will remove all the entries that are not 
      shown anymore inside the local file system or the central repository. 
      This is usefull to understand that a file has been deleted. 

      :param repo: Reference to the pointer so to update it with the information 
     
  */
  void ScriptRepositoryImpl::parseDownloadedEntries(Repository & repo){
    ptree pt; 
    std::string filename = std::string(local_repository).append(".local.json");
    std::vector<std::string> entries_to_delete;
    Repository::iterator entry_it;
    try{
      read_json(filename, pt);
      BOOST_FOREACH(ptree::value_type & file, pt){
        entry_it = repo.find(file.first);        
        if (entry_it != repo.end()){
          // entry found, so, lets update the entry
          if (entry_it->second.local && entry_it->second.remote){
            // this is the normal condition, the downloaded entry
            // was found at the local file system and at the remote repository

            entry_it->second.downloaded_pubdate = DateAndTime(file.second.get<std::string>("downloaded_pubdate"));
            entry_it->second.downloaded_date = DateAndTime(file.second.get<std::string>("downloaded_date"));


          }else{
            // if the entry was not found locally or remotelly, this means 
            // that this entry was deleted (remotelly or locally), 
            // so it should not appear at local_repository json any more
            entries_to_delete.push_back(file.first);
          }
        }else{
          // this entry was never created before, so it should not
          // exist in local repository json
          entries_to_delete.push_back(file.first);
        }
        
      }// end loop FOREACH entry in local json

      // delete the entries to be deleted in json file
      if (entries_to_delete.size() > 0){
        for (std::vector<std::string>::iterator it = entries_to_delete.begin();
             it != entries_to_delete.end();
             it++){
          // remove this entry
          pt.erase(*it);
        }
#if defined(_WIN32) ||  defined(_WIN64)
        //set the .repository.json and .local.json not hidden (to be able to edit it)
        SetFileAttributes( filename.c_str(), FILE_ATTRIBUTE_NORMAL);     
#endif
        write_json(filename,pt);
#if defined(_WIN32) ||  defined(_WIN64)
        //set the .repository.json and .local.json hidden
        SetFileAttributes( filename.c_str(), FILE_ATTRIBUTE_HIDDEN);     
#endif
      }
    }catch (boost::property_tree::json_parser_error & ex){
      std::stringstream ss;
      ss << "Corrupted local database : " << filename; 
      
      g_log.error() << "ScriptRepository: " << ss.str() 
                    << "\nDetails: downloaded entries - json_parser_error: " << ex.what() << std::endl; 
      throw ScriptRepoException(ss.str(), ex.what()); 
    }catch(std::exception & ex){
      std::stringstream ss; 
      ss << "RuntimeError: checking downloaded entries >> " << ex.what();
      g_log.error() << "ScriptRepository: " << ss.str() << ". Input: " << filename << std::endl;
      throw ScriptRepoException(ss.str(), filename); 
    }catch(...){
      g_log.error() << "FATAL Unknown error (checking downloaded entries): " << filename << std::endl;
      throw;
    }   
  }
  
  void ScriptRepositoryImpl::updateLocalJson(const std::string & path, const RepositoryEntry & entry){
    ptree local_json; 
    std::string filename = std::string(local_repository).append(".local.json");
    read_json(filename, local_json); 

    ptree::const_assoc_iterator it = local_json.find(path);
    if (it == local_json.not_found()){
      boost::property_tree::ptree array;
      array.put(std::string("downloaded_date"), entry.downloaded_date.toFormattedString());
      array.put(std::string("downloaded_pubdate"), entry.downloaded_pubdate.toFormattedString());
      //      array.push_back(std::make_pair("auto_update",entry.auto_update)));
      local_json.push_back( std::pair<std::string, boost::property_tree::basic_ptree<std::string,std::string> >(path,array) );
    }else{
      local_json.put(std::string(path).append(".downloaded_pubdate"), 
                     entry.downloaded_pubdate.toFormattedString());
    }
    //g_log.debug() << "Update LOCAL JSON FILE" << std::endl; 
    #if defined(_WIN32) ||  defined(_WIN64)
    //set the .repository.json and .local.json not hidden to be able to edit it
    SetFileAttributes( filename.c_str(), FILE_ATTRIBUTE_NORMAL);     
    #endif
    write_json(filename, local_json); 
    #if defined(_WIN32) ||  defined(_WIN64)
    //set the .repository.json and .local.json hidden
    SetFileAttributes( filename.c_str(), FILE_ATTRIBUTE_HIDDEN);     
    #endif
  }


  std::string ScriptRepositoryImpl::printStatus(SCRIPTSTATUS st){
    switch(st){
    case BOTH_UNCHANGED:
      return "Unchanged"; 
    case LOCAL_ONLY:
      return "LocalOnly"; 
    case LOCAL_CHANGED:
      return "LocalChanged"; 
    case REMOTE_ONLY:
      return "RemoteOnly"; 
    case REMOTE_CHANGED:
      return "RemoteChanged";
    case BOTH_CHANGED:
      return "BothChanged";
    default:
      return "FAULT: INVALID STATUS";     
    }
      return "FAULT: INVALID STATUS";     
  }
  /** 
      @todo describe
  */
  void ScriptRepositoryImpl::recursiveParsingDirectories(const std::string & path,
                                                         Repository & repo){
    using Poco::DirectoryIterator;
    DirectoryIterator end;
    try{
      for (DirectoryIterator it(path); it != end; ++it){
        std::string entry_path = convertPath(it->path()); 
        
        if (!isEntryValid(entry_path))
          continue;
        
        
        //g_log.debug() << "RecursiveParsing: insert : " << entry_path << std::endl; 
        RepositoryEntry & entry = repo[entry_path]; 
        entry.local = true; 
        entry.current_date = DateAndTime(
                                         Poco::DateTimeFormatter::format(it->getLastModified(),
                                                                         timeformat)); 
        entry.directory = it->isDirectory(); 
        if (it->isDirectory())
          recursiveParsingDirectories(it->path(),repo);
      }
    }catch(Poco::Exception & ex){
      g_log.error() << "ScriptRepository: failed to parse the directory: " << path << " : "
                    << ex.className() << " : " << ex.displayText() << std::endl; 
      // silently ignore this exception.
      // throw ScriptRepoException(ex.displayText()); 
    }catch(std::exception & ex){
      std::stringstream ss; 
      ss << "unknown exception while checking local file system. " << ex.what() << ". Input = " << path ;
      g_log.error() << "ScriptRepository: " << ss.str() << std::endl; 
      throw ScriptRepoException(ss.str()); 
    }
  }

  bool ScriptRepositoryImpl::isEntryValid(const std::string & path){
    //g_log.debug() << "Is valid entry? " << path << std::endl; 
    if (path == ".repository.json")
      return false;
    if (path == ".local.json")
      return false;
    // hide everything under system folder
    if (path == "system" || path.find("system/") == 0)
      return false; 

    try{
      boost::regex re1(ignoreregex);
    
      if (boost::regex_match(path,re1))
      return false;
    // TODO: apply the pattern ingore checking
    }catch(std::exception & ex){
      g_log.warning() << "Pattern exception : " << ignoreregex << ": "
                      << ex.what() << std::endl; 
    }
    return true;
  }

  /**
     Transform the file path in a path related to the local repository.
     Set the flag file_is_local to true if the file already exists inside
     the local machine.
     
     For example: 
     
     @code 
     // consider the local repository at /opt/scripts_repo/
     bool flag; 
     convertPath("/opt/scripts_repo/README.md", flag) // returns: README.md
     convertPath("README.md", flag) // returns: README.md
     // consider the local repository at c:\MantidInstall\scripts_repo
     convertPath("c:\MantidInstall\scripts_repo\README.md", flag)// returns README.md
     @endcode
  */
  std::string ScriptRepositoryImpl::convertPath(const std::string & path){
    std::vector<std::string> lookAfter; 
    using Poco::Path;
    lookAfter.push_back(Path::current()); 
//    lookAfter.push_back(Path::home()); 
    lookAfter.push_back(local_repository); 
  
    Path pathFound; 
    bool file_is_local;

    // try to find the given path at one of the paths at lookAfter.
    file_is_local = Path::find(lookAfter.begin(), lookAfter.end(), path, pathFound);
    // get the absolute path: 
    std::string absolute_path;
    if (file_is_local)      
      absolute_path = pathFound.absolute().toString(); 
    else
      absolute_path = path;
    //g_log.debug() << "ConvertPath: Entered: " << path  << " and local_repository: " << local_repository << std::endl; 
    // this is necessary because in windows, the absolute path is given with \ slash.
    boost::replace_all(absolute_path,"\\","/");     
    
    //check it the path is inside the repository: 
    size_t pos = absolute_path.find(local_repository); 

    if (pos == std::string::npos){      
      // the given file is not inside the local repository. It can not be converted.
      return path; 
    }else{
      // the path is inside the local repository
      // remove the repo_path from te absolute path 
      // +1 to remove the slash /      
      std::string retpath(absolute_path.begin() + pos + local_repository.size(), absolute_path.end()); 
      //g_log.debug() << "ConvertPath: Entered: " << path << " return: " << retpath << std::endl; 
      return retpath;
    }
    return path; 
  }


}// END API
}// END MANTID




# $HeadURL $
''' ResourceStatusDB

  Module that provides basic methods to access the ResourceStatusDB.

'''

from datetime                             import datetime 

from DIRAC                                import S_OK, S_ERROR 
from DIRAC.Core.Base.DB                   import DB
from DIRAC.ResourceStatusSystem.Utilities import MySQLWrapper, RssConfiguration

__RCSID__ = '$Id: $'

class ResourceStatusDB( object ):
  
  # Written PrimaryKey as list on purpose !!
  __tablesDB = {}
  
  __tablesLike = {}
  __tablesLike[ 'ElementStatus' ]    = { 'Fields' : 
                    {
                     'Name'            : 'VARCHAR(64) NOT NULL',
                     'StatusType'      : 'VARCHAR(16) NOT NULL DEFAULT ""',
                     'Status'          : 'VARCHAR(8) NOT NULL DEFAULT ""',
                     'ElementType'     : 'VARCHAR(32) NOT NULL DEFAULT ""',
                     'Reason'          : 'VARCHAR(255) NOT NULL DEFAULT "Unspecified"',
                     'DateEffective'   : 'DATETIME NOT NULL',
                     'LastCheckTime'   : 'TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP',
                     'TokenOwner'      : 'VARCHAR(16) NOT NULL DEFAULT "rs_svc"',
                     'TokenExpiration' : 'DATETIME NOT NULL DEFAULT "9999-12-31 23:59:59"'
                    },
                    'PrimaryKey' : [ 'Name', 'StatusType', 'ElementType' ]              
                                    }
    
  __tablesLike[ 'ElementWithID' ]       = { 'Fields' : 
                    {
                     'ID'              : 'INT UNSIGNED AUTO_INCREMENT NOT NULL',
                     'Name'            : 'VARCHAR(64) NOT NULL',
                     'StatusType'      : 'VARCHAR(16) NOT NULL DEFAULT ""',
                     'Status'          : 'VARCHAR(8) NOT NULL DEFAULT ""',
                     'ElementType'     : 'VARCHAR(32) NOT NULL DEFAULT ""',
                     'Reason'          : 'VARCHAR(255) NOT NULL DEFAULT "Unspecified"',
                     'DateEffective'   : 'DATETIME NOT NULL',
                     'LastCheckTime'   : 'TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP',
                     'TokenOwner'      : 'VARCHAR(16) NOT NULL DEFAULT "rs_svc"',
                     'TokenExpiration' : 'DATETIME NOT NULL DEFAULT "9999-12-31 23:59:59"'
                    },
                    'PrimaryKey' : [ 'ID' ]                
                                    }

  __likeToTable = { 
                    'SiteStatus'        : 'ElementStatus',
                    'SiteLog'           : 'ElementWithID',
                    'SiteHistory'       : 'ElementWithID',
                    'SiteScheduled'     : 'ElementWithID',
                    'ResourceStatus'    : 'ElementStatus',
                    'ResourceLog'       : 'ElementWithID',
                    'ResourceHistory'   : 'ElementWithID',
                    'ResourceScheduled' : 'ElementWithID',
                    'NodeStatus'        : 'ElementStatus',
                    'NodeLog'           : 'ElementWithID',
                    'NodeHistory'       : 'ElementWithID',      
                    'NodeScheduled'     : 'ElementWithID'             
                   }

# No idea whether they make sense or not
#  __tables[ 'ElementPresent' ]   = {} #????  
#  __tables[ 'Element' ]          = {} #????
  
  def __init__( self, maxQueueSize = 10, mySQL = None ):
    '''
      Constructor, accepts any DB or mySQL connection, mostly used for testing
      purposes.
    '''

    self._tableDict = self.__generateTables()
    
    if mySQL is not None:
      self.database = mySQL
    else:
      self.database = DB( 'ResourceStatusDB', 
                          'ResourceStatus/ResourceStatusDB', maxQueueSize )  

    self.recordLogs = RssConfiguration.getRecordLogs()

  ## SQL Methods ###############################################################

  def insert( self, params, meta ):
    '''
    Inserts args in the DB making use of kwargs where parameters such as
    the 'table' are specified ( filled automatically by the Client). Typically you 
    will not pass kwargs to this function, unless you know what are you doing 
    and you have a very special use case.

    :Parameters:
      **params** - `dict`
        arguments for the mysql query ( must match table columns ! ).

      **meta** - `dict`
        metadata for the mysql query. It must contain, at least, `table` key
        with the proper table name.

    :return: S_OK() || S_ERROR()
    '''
    return MySQLWrapper.insert( self, params, meta )

  def update( self, params, meta ):
    '''
    Updates row with values given on args. The row selection is done using the
    default of MySQLMonkey ( column.primary or column.keyColumn ). It can be
    modified using kwargs. The 'table' keyword argument is mandatory, and 
    filled automatically by the Client. Typically you will not pass kwargs to 
    this function, unless you know what are you doing and you have a very 
    special use case.

    :Parameters:
      **params** - `dict`
        arguments for the mysql query ( must match table columns ! ).

      **meta** - `dict`
        metadata for the mysql query. It must contain, at least, `table` key
        with the proper table name.

    :return: S_OK() || S_ERROR()
    '''
    return MySQLWrapper.update( self, params, meta )

  def select( self, params, meta ):
    '''
    Uses arguments to build conditional SQL statement ( WHERE ... ). If the
    sql statement desired is more complex, you can use kwargs to interact with
    the MySQL buildCondition parser and generate a more sophisticated query.

    :Parameters:
      **params** - `dict`
        arguments for the mysql query ( must match table columns ! ).

      **meta** - `dict`
        metadata for the mysql query. It must contain, at least, `table` key
        with the proper table name.

    :return: S_OK() || S_ERROR()
    '''
    return MySQLWrapper.select( self, params, meta )

  def delete( self, params, meta ):
    '''
    Uses arguments to build conditional SQL statement ( WHERE ... ). If the
    sql statement desired is more complex, you can use kwargs to interact with
    the MySQL buildCondition parser and generate a more sophisticated query. 
    There is only one forbidden query, with all parameters None ( this would 
    mean a query of the type `DELETE * from TableName` ). The usage of kwargs 
    is the same as in the get function.

    :Parameters:
      **params** - `dict`
        arguments for the mysql query ( must match table columns ! ).

      **meta** - `dict`
        metadata for the mysql query. It must contain, at least, `table` key
        with the proper table name.

    :return: S_OK() || S_ERROR()
    '''
    return MySQLWrapper.delete( self, params, meta )

  ## Extended SQL methods ######################################################
  
  def addOrModify( self, params, meta ):
    '''
    Using the PrimaryKeys of the table, it looks for the record in the database.
    If it is there, it is updated, if not, it is inserted as a new entry. 
    
    :Parameters:
      **params** - `dict`
        arguments for the mysql query ( must match table columns ! ).

      **meta** - `dict`
        metadata for the mysql query. It must contain, at least, `table` key
        with the proper table name.

    :return: S_OK() || S_ERROR()
    '''
        
    selectQuery = self.select( params, meta )
    if not selectQuery[ 'OK' ]:
      return selectQuery 
       
    isUpdate = False
       
    if selectQuery[ 'Value' ]:      
      userQuery  = self.update( params, meta )
      isUpdate   = True
    else:      
      if 'dateEffective' in params and params[ 'dateEffective' ] is None:
        params[ 'dateEffective' ] = datetime.now().replace( microsecond = 0 )
      userQuery = self.insert( params, meta )
    
    if self.recordLogs:
      
      if 'table' in meta and meta[ 'table' ].endswith( 'Status' ):
        
        if isUpdate:
          updateRes = self.select( params, meta )
          if not updateRes[ 'OK' ]:
            return updateRes
          
          # If we are updating more that one result at a time, this is most likely
          # going to be a mess. All queries must be one at a time, if need to do
          if len( updateRes[ 'Value' ] ) != 1:
            return S_ERROR( ' PLEASE REPORT to developers !!: %s, %s' % ( params, meta ) )
          if len( updateRes[ 'Value' ][ 0 ] ) != len( updateRes[ 'Columns' ] ):
            # Uyyy, something went seriously wrong !!
            return S_ERROR( ' PLEASE REPORT to developers !!: %s' % updateRes )
                    
          params = dict( zip( updateRes['Columns'], updateRes[ 'Value' ][0] )) 
                
        meta[ 'tableName' ] = meta[ 'tableName' ].replace( 'Status', 'Log' )

        logRes = self.insert( params, meta )
        if not logRes[ 'OK' ]:
          return logRes
    
    return userQuery      

  def addIfNotThere( self, params, meta ):
    '''
    Using the PrimaryKeys of the table, it looks for the record in the database.
    If it is not there, it is inserted as a new entry. 
    
    :Parameters:
      **params** - `dict`
        arguments for the mysql query ( must match table columns ! ).

      **meta** - `dict`
        metadata for the mysql query. It must contain, at least, `table` key
        with the proper table name.

    :return: S_OK() || S_ERROR()
    '''
        
    selectQuery = self.select( params, meta )
    if not selectQuery[ 'OK' ]:
      return selectQuery 
       
    if selectQuery[ 'Value' ]:      
      return selectQuery
    
    if 'dateEffective' in params and params[ 'dateEffective' ] is None:
      params[ 'dateEffective' ] = datetime.now().replace( microsecond = 0 )
    
    return self.insert( params, meta )      

  ## Auxiliar methods ##########################################################

  def getTable( self, tableName ):
    '''
      Returns a table dictionary description given its name 
    '''
    if tableName in self._tableDict:
      return S_OK( self._tableDict[ tableName ] )
    
    return S_ERROR( '%s is not on the schema' % tableName )
    
  def getTablesList( self ):
    '''
      Returns a list of the table names in the schema.
    '''
    return S_OK( self._tableDict.keys() )

  ## Protected methods #########################################################

  def _checkTable( self ):
    '''
      Method used by database tools to write the schema
    '''  
    return self.__createTables()

  def _logRecord( self, params, meta ):
    pass
#    # No more processing on for select and delete queries
#    if queryType in [ 'select', 'delete' ]:
#      return userRes
#    
#    # If something went wrong, we return
#    if not userRes[ 'OK' ]:
#      return userRes
#
#    # If the operation is on a table different than 'Status', we return
#    if not tableType == 'Status':
#      return userRes
#    
#    # If the flag is active, we record this entry on the <element>Log table
#    if self.__recordLogs:
#      logRes = self.insertStatusElement( element, 'Log', meta = meta, **parameters )
#      if not logRes[ 'OK' ]:
#        gLogger.error( '%s inserting log' % logRes[ 'Message' ] )    

  ## Private methods ###########################################################

  def __createTables( self, tableName = None ):
    '''
      Writes the schema in the database. If no tableName is given, all tables
      are written in the database. If a table is already in the schema, it is
      skipped to avoid problems trying to create a table that already exists.
    '''

    # Horrible SQL here !!
    tablesCreatedRes = self.database._query( "show tables" )
    if not tablesCreatedRes[ 'OK' ]:
      return tablesCreatedRes
    tablesCreated = [ tableCreated[0] for tableCreated in tablesCreatedRes[ 'Value' ] ]

    tables = {}
    if tableName is None:
      tables.update( self._tableDict )
   
    elif tableName in self._tableDict:
      tables = { tableName : self._tableDict[ tableName ] }
    
    else:
      return S_ERROR( '"%s" is not a known table' % tableName )    
      
    for tableName in tablesCreated:
      if tableName in tables:
        del tables[ tableName ]  
              
    res = self.database._createTables( tables )
    if not res[ 'OK' ]:
      return res
    
    # Human readable S_OK message
    if res[ 'Value' ] == 0:
      res[ 'Value' ] = 'No tables created'
    else:
      res[ 'Value' ] = 'Tables created: %s' % ( ','.join( tables.keys() ) )
    return res       

  def __generateTables( self ):
    '''
      Method used to transform the class variables into instance variables,
      for safety reasons.
    '''
  
    # Avoids copying object.
    tables = {}
    tables.update( self.__tablesDB )
    
    for tableName, tableLike in self.__likeToTable.items():
      
      tables[ tableName ] = self.__tablesLike[ tableLike ]
       
    return tables
    
################################################################################
#EOF#EOF#EOF#EOF#EOF#EOF#EOF#EOF#EOF#EOF#EOF#EOF#EOF#EOF#EOF#EOF#EOF#EOF#EOF#EOF   
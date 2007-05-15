#!/usr/bin/env python2.4
# $Header: /tmp/libdirac/tmp.stZoy15380/dirac/DIRAC3/DIRAC/Core/Base/Attic/DiracScript.py,v 1.1 2007/05/15 13:12:34 acasajus Exp $
__RCSID__ = "$Id: DiracScript.py,v 1.1 2007/05/15 13:12:34 acasajus Exp $"

import sys
from dirac import DIRAC
from DIRAC.ConfigurationSystem.Client.LocalConfiguration import LocalConfiguration
from DIRAC.LoggingSystem.Client.Logger import gLogger

localCfg = LocalConfiguration()

scriptName = sys.argv[0]
serverSection = localCfg.setConfigurationForScript( scriptName )
localCfg.addMandatoryEntry( "/DIRAC/Setup" )
resultDict = localCfg.loadUserData()
if not resultDict[ 'OK' ]:
  gLogger.error( "There were errors when loading configuration", resultDict[ 'Message' ] )
  sys.exit(1)

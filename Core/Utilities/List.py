# $Header: /tmp/libdirac/tmp.stZoy15380/dirac/DIRAC3/DIRAC/Core/Utilities/List.py,v 1.3 2007/05/14 16:22:39 gkuznets Exp $
__RCSID__ = "$Id: List.py,v 1.3 2007/05/14 16:22:39 gkuznets Exp $"
"""
   Collection of DIRAC useful list related modules
   by default on Error they return None
"""

from types import StringTypes
import random
random.seed()

def uniqueElements( list ):
  """
     Utility to retrieve list of unique elements in a list (order is kept)
  """
  newList = []
  try:
    for i in list:
      if i not in newList:
        newList.append( i )
    return newList
  except:
    return None

def fromChar( inputString, sepChar = "," ):
  """
     Generates a list splitting a string by the required character(s)
     resulting string items are stripped and empty items are removed
  """
  if not ( type( inputString ) in StringTypes and
           type( sepChar ) in StringTypes and
           sepChar ): # to prevent getting an empty String as argument
    return None

  return [ fieldString.strip() for fieldString in inputString.split( sepChar ) if len( fieldString.strip() ) > 0 ]

def randomize( initialList ):
  """
  Return a randomly sorted list
  """
  #A index list is built so the initial list is left untouched
  indexList = range( len( initialList ) )
  randomList = []
  while len( indexList ) > 0:
    randomPos = random.randrange( len( indexList ) )
    randomList.append( initialList[ indexList[ randomPos ] ] )
    del( indexList[ randomPos ] )
  return randomList

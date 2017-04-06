"""
   process_plotsafe_data
   
   Applies various data transformations to a PlotSafe XML data file.

     1. Restructure strata/plots (option -s) from one stratum containing all plots, to one strata per plot

   v1.0
   v1.1 Cope with missing description on stratum
 
         
   BCC
   FII, Scion
   April 2017

"""

import getopt
import sys
import xml.dom.minidom


# Globals
inputFile  = ""
outputFile = ""
restructurePlots = False

def GetPlotName( plotElement ):
    return plotElement.firstChild.nodeValue


def addTextNode( dom, node, text ):
    textNode = dom.createTextNode( text )
    node.appendChild( textNode )


def addChildElementWithText( dom, parentNode, elementName, textContent ):
    """ Creates a new element with the given text content, and adds it to the node. """
    
    newElement = dom.createElement( elementName )
    addTextNode( dom, newElement, textContent )
    parentNode.appendChild( newElement )


def createStratum( dom, name, description, area, timeLastModified ):
    """ Creates a new stratum, sets its base elements, and returns it. """
    
    newStratum = dom.createElement( "stratum" )

    addChildElementWithText( dom, newStratum, "stratum_name",       name )
    addChildElementWithText( dom, newStratum, "stratum_area",       str( area ) )
    addChildElementWithText( dom, newStratum, "time_last_modified", str( timeLastModified ) )
    if ( len( description ) > 0 ):
        addChildElementWithText( dom, newStratum, "description",    description )

    return newStratum


def renameStrata( dom ):
    """ Creates one stratum for each plot """

    # Find the original stratum, and get its attributes and contents
    strata = dom.getElementsByTagName( "strata" )
    if ( strata.length != 1 ):
        raise Exception( "Not exactly 1 <strata> element" )
    stratumNode = strata[0]
    stratums = stratumNode.getElementsByTagName( "stratum" )
    if ( stratums.length != 1 ):
        raise Exception( "Not exactly 1 <stratum> element" )
    originalStratum = stratums[0]
    stratumDescription = ""
    descrElems = originalStratum.getElementsByTagName( "description" )
    if ( len( descrElems ) > 0 ):
        stratumDescription = descrElems[0].firstChild.nodeValue

    stratumArea        = originalStratum.getElementsByTagName( "stratum_area" )[0].firstChild.nodeValue
    stratumTimeLastMod = originalStratum.getElementsByTagName( "time_last_modified" )[0].firstChild.nodeValue
    plots = originalStratum.getElementsByTagName( "plot" )
    
    # For each plot, create a new stratum with the plot's name, and move the plot into it
    for plot in plots:
        names = plot.getElementsByTagName( "plot_name" )
        if ( names.length != 1 ):
            raise Exception( "This plot does not have exactly 1 <plot_name> element (so what is its name?)" )

        newStratum = createStratum( dom, GetPlotName( names[0] ), stratumDescription, 0, stratumTimeLastMod )
        stratumNode.appendChild( newStratum )

        plotsElement = dom.createElement( "plots" )
        plotsElement.appendChild( plot ) # N.B. this does a move, not a copy
        newStratum.appendChild( plotsElement )
 
    # Throw away the original stratum
    stratumNode.removeChild( originalStratum )
    print ( )
    print ( plots.length, "plots processed" )
    print ( )


def acknowledge( dom ):
    """ Add root-level comments, before and/or after the root element """

    openingComment = "This file has been modified to have 1 stratum per plot"
    #dom.insertBefore( dom.createComment( openingComment ), dom.documentElement )
    #dom.appendChild(  dom.createComment( "This is a closing comment" ) )


def usage():
    print ( "" )
    print ( "usage: process_plotsafe_data.py -i<inputfile> -o<outputfile> [OPTIONS]" )
    print ( "" )
    print ( "  inputfile               Input XML file (full path)" )
    print ( "  outputfile              Output XML file (full path)" )
    print ( "  OPTIONS" )
    print ( "   -h, --help             Print usage message, and exit" )
    print ( "   -s                     Restructure strata - from one only, to one per plot" )
    print ( "" )


def processArguments():
    """ Interprets the command-line arguments """

    global inputFile
    global outputFile
    global restructurePlots

    if ( len( sys.argv ) == 1 ):
        usage()
        sys.exit()

    opts, args = getopt.getopt( sys.argv[1:], "?hsi:o:", [ "infile=", "outfile=", "help" ] )

    for opt, arg in opts:
        if opt in ( "-h", "-?", "--help" ):
            usage()
            sys.exit()
        elif opt in ( "-s" ):
            restructurePlots = True
        elif opt in ( "-i", "--infile" ):
            inputFile = arg
        elif opt in ( "-o", "--outfile" ):
            outputFile = arg

    if len( inputFile ) == 0:      
        raise Exception( "No input file specified" )
    if len( outputFile ) == 0:      
        raise Exception( "No output file specified" )

    print( )
    print( "Input file: ", inputFile )
    print( "Output file:", outputFile )


def main():

    print ( sys.version )

    try:
        processArguments()
    except Exception as excArg:
        print( "Error processing commmand line arguments:", excArg )
        sys.exit( 4201 )

    try:
        dom = xml.dom.minidom.parse( inputFile )
        if ( restructurePlots ):
            renameStrata( dom )
            acknowledge( dom ) 
    except Exception as exc:
        print( "Error processing reading and processing XML:", exc )
        sys.exit( 4202 )


    try:
        fOut = open( outputFile, "w" )
        dom.writexml( fOut )
        fOut.close()
    except Exception as exc:
        print( "Error writing XML", exc )
        sys.exit( 4203 )



if __name__ == "__main__":
   main()
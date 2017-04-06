import csv
import glob
import logging
import os
import sys

DataPath = "C:\\Data\\Sonic Data\\22-03-17"

okfileName = "C:\\Data\\Sonic Data\\24-02-17\\TOA5_3894.SonicData_1208_2017_02_24_0000.dat"
badfileName = "C:\\Data\\Sonic Data\\17-02-17\\TOA5_3894.SonicData_871_2017_02_17_0000.dat"


def DoStuff():

    logging.basicConfig( 
        #filename="D:\\test2017\\test01.log", 
        level=logging.DEBUG, 
        format="%(asctime)s.%(msecs)03d %(levelname)8s %(message)s", 
        datefmt="%Y-%m-%d %H:%M:%S" )

    logging.info( "This is an Info msg" )
    logging.warning( "This is a Warning msg" )

"""
"  Processes the single specified record, and returns True if its data is "clean", otherwise False
"""
def ProcessARecord( record ):

    failCodes = [ False, False, False, False, False ]
    # Check that all 5 diagnostic codes are 0 (actually "0" - they're strings)
    #if ( record[ "Diag_1" ] != "0" or record[ "Diag_2" ] != "0" or record[ "Diag_3" ] != "0" or record[ "Diag_4" ] != "0" or record[ "Diag_5" ] != "0"  ):
    #    return False

    # Check and return each code separately
    if ( record[ "Diag_1" ] != "0" ):
        failCodes[0] = True
    if ( record[ "Diag_2" ] != "0" ):
        failCodes[1] = True
    if ( record[ "Diag_3" ] != "0" ):
        failCodes[2] = True
    if ( record[ "Diag_4" ] != "0" ):
        failCodes[3] = True
    if ( record[ "Diag_5" ] != "0" ):
        failCodes[4] = True

    return failCodes


"""
"  Processes the specified file, and returns True if all of its rows are "clean", otherwise False
"""
def ProcessAFile( fileName, summaryFile ):

    print ( "Processing file", fileName )

    csvFile = open( fileName, newline='' )

    # Cope with the 4-line header (!)
    line1 = csvFile.readline()
    line2 = csvFile.readline()
    line3 = csvFile.readline()
    line4 = csvFile.readline()

    # Extract the column headers
    headerLine = line2.replace( "\"", "" )
    headers    = headerLine[:len( headerLine ) - 2 ].split( ',' ) # trim eol, and separate the items

    # Create a reader, and process all data records in the file
    csvReader = csv.DictReader( csvFile, headers )

    totalRecords = 0
    badRecords   = 0
    diagCount    = [ 0, 0, 0, 0, 0 ]

    for record in csvReader:
        totalRecords += 1
        failCodes = ProcessARecord( record )

        # Check for *any* bad diagnostic code  
        if ( True in failCodes ):  
            badRecords += 1
            for idx in  [0, 1, 2, 3, 4 ]:
                if ( failCodes[ idx ] ):
                    diagCount[ idx ] += 1

    print ( badRecords, "of", totalRecords, "records have error(s)\n" )
    summaryFile.write( os.path.split( fileName )[1] + ", "
                      + str( badRecords ) + ", "
                      + str( diagCount[ 0 ] ) + ", " 
                      + str( diagCount[ 1 ] ) + ", " 
                      + str( diagCount[ 2 ] ) + ", " 
                      + str( diagCount[ 3 ] ) + ", " 
                      + str( diagCount[ 4 ] ) + "\n" )

    return ( badRecords == 0 )
 
       
"""
"  Processes the specified folder - scans all contained files, and reports on how many are "clean"
"""
def ProcessAFolder( folderPath ):

    if ( not os.path.isdir( folderPath ) ):
        print( "The folder", folderPath, "could not be found" )
        return

    outputFile = open( os.path.join( folderPath, "FileSummary.csv" ), 'w' )
    outputFile.write( "file name,# bad records,# bad 'Diag_1',# bad 'Diag_2',# bad 'Diag_3',# bad 'Diag_4',# bad 'Diag_5'\n" )

    totalFiles = 0
    badFiles   = 0
    for file in os.listdir( folderPath ):
        fileSpec = os.path.join( folderPath, file )
       
        if ( os.path.splitext( file )[1] != ".dat" ):
            continue  # skip any non-data files

        if ( os.path.isfile( fileSpec ) ):
            totalFiles += 1
            if ( not ProcessAFile ( fileSpec, outputFile ) ):
                badFiles += 1

    outputFile.close()
    print ( "Summary for folder", folderPath, "\n" )
    print ( badFiles, "of", totalFiles, "files have error(s)" )
    print ( )
    print ( "An error is (currently) defined as a record having *any* of its 5 diagnostic codes non-zero." )


def Main( argv ):

    if ( len( argv ) < 2 ):
        print()
        folderName = input( "Enter the folder to check (as a full path, e.g. D:\\Data\\Sonic Data\\17-02-17): ")

    print()

    ProcessAFolder( folderName )

    print()


if ( __name__ == "__main__" ):

    Main( sys.argv )


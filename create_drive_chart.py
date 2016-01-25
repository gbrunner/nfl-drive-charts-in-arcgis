#-------------------------------------------------------------------------------
# Name:        create_drive_chart.py
# Purpose:
#
# Author:      Gregory Brunner, Esri
#
# Created:     14/01/2016
# Copyright:   (c) greg6750 2016
# Licence:     <your licence>
#-------------------------------------------------------------------------------

import os

import nflgame
from nflgame import seq as seq

import arcpy

drive_fields = ('SHAPE@','TEAM','DRIVE_NUM','START_POS', 'END_POS', 'DURATION', 'RESULT', 'DESCRIPTION')
play_fields = ('SHAPE@', 'TEAM')

def create_drive_feature_class(output_gdb, output_feature_class):
    feature_class = os.path.basename(output_feature_class)
    if not arcpy.Exists(output_gdb):
        arcpy.CreateFileGDB_management(os.path.dirname(output_gdb),os.path.basename(output_gdb))

    fc = os.path.join(output_gdb,output_feature_class)
    if not arcpy.Exists(os.path.join(output_gdb,output_feature_class)):
        #"PROJCS['WGS_1984_Web_Mercator_Auxiliary_Sphere',GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137.0,298.257223563]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Mercator_Auxiliary_Sphere'],PARAMETER['False_Easting',0.0],PARAMETER['False_Northing',0.0],PARAMETER['Central_Meridian',0.0],PARAMETER['Standard_Parallel_1',0.0],PARAMETER['Auxiliary_Sphere_Type',0.0],UNIT['Meter',1.0]]", transform_method="", in_coor_system="GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137.0,298.257223563]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]]"
        arcpy.CreateFeatureclass_management(output_gdb,output_feature_class,"POLYGON","#","DISABLED","DISABLED", "PROJCS['WGS_1984_Web_Mercator_Auxiliary_Sphere',GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137.0,298.257223563]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Mercator_Auxiliary_Sphere'],PARAMETER['False_Easting',0.0],PARAMETER['False_Northing',0.0],PARAMETER['Central_Meridian',0.0],PARAMETER['Standard_Parallel_1',0.0],PARAMETER['Auxiliary_Sphere_Type',0.0],UNIT['Meter',1.0]]","#","0","0","0")
        arcpy.AddField_management(fc, drive_fields[1],"TEXT", "", "", 10)
        arcpy.AddField_management(fc, drive_fields[2],"TEXT", "", "", 10)
        arcpy.AddField_management(fc, drive_fields[3],"TEXT", "", "", 100)
        arcpy.AddField_management(fc, drive_fields[4],"TEXT", "", "", 100)
        arcpy.AddField_management(fc, drive_fields[5],"TEXT", "", "", 100)
        arcpy.AddField_management(fc, drive_fields[6],"TEXT", "", "", 100)
        arcpy.AddField_management(fc, drive_fields[7],"TEXT", "", "", 100)

def create_chart_polygon(drive, home, away):
    #start = drive.field_start
    #end_ = drive.field_end
    #start_location = start.split(' ')
    #end_location = end.split(' ')

    scale_by = 10
    if drive.team == home:
        start_x = 50 + drive.field_start.__dict__['offset']
        if drive.result == 'Touchdown':
            end_x = 100
        else:
            end_x = 50 + drive.field_end.__dict__['offset']

    if drive.team == away:
        start_x = 50 - drive.field_start.__dict__['offset']
        if drive.result == 'Touchdown':
            end_x = 0
        else:
            end_x = 50 - drive.field_end.__dict__['offset']

    return scale_by*start_x,scale_by*end_x

def get_game_drives(game):

    return [drive for drive in game.drives]



def get_drive_plays(drive):

    return [play for play in drive.plays]

def create_drive_polygons(fc, drives):

    cursor = arcpy.da.InsertCursor(fc, ["SHAPE@"])
    for drive in drives:
        array = arcpy.Array([arcpy.Point(5997611.48964, 2069897.7022),
                     arcpy.Point(5997577.46097, 2069905.81145)])
        polygon= arcpy.Polygon(array)

        cursor.insertRow([polygon])

def populate_feature_class(rowValues, output_feature_class):
    #rowValues = [('Anderson', (1409934.4442000017, 1076766.8192000017))]
    c = arcpy.da.InsertCursor(output_feature_class,fc_fields)
    for row in rowValues:
        #print(row)
        c.insertRow(row)
    del c

def main(ome, away, year, week, output_gdb, output_fc):
    game = nflgame.one(year, week, home,away)

    print('Create drive feature class.')
    create_drive_feature_class(output_gdb, output_fc)

    print('Getting drive data.')
    drives = get_game_drives(game)

    print('Opening insert cursor.')
    cursor = arcpy.da.InsertCursor(os.path.join(output_gdb, output_fc),drive_fields)# ["SHAPE@"])#drive_fields)

    for drive in drives:
        start_x, end_x = create_chart_polygon(drive, home, away)
        array = arcpy.Array([arcpy.Point(start_x, drive.drive_num*10),
                     arcpy.Point(end_x, drive.drive_num*10),
                     arcpy.Point(end_x, drive.drive_num*10+9),
                     arcpy.Point(start_x, drive.drive_num*10+9)])
        polygon= arcpy.Polygon(array)

        print(str(drive))
        cursor.insertRow([polygon, drive.team, drive.drive_num, str(drive.field_start),str(drive.field_end),str(drive.pos_time.__dict__['minutes']) + ' min and ' + str(drive.pos_time.__dict__['seconds']) + ' sec', drive.result, str(drive)])

    print('Done.')


        #plays = get_drive_plays(drive)
        #for play in plays:
          #  print(play)
           # print(play.rushing_yds)
            #print(play.time)


if __name__ == '__main__':
    home = 'PIT'
    away = 'DEN'
    year = 2015
    week = 15
    output_gdb = "C:/NFL/game.gdb"
    output_fc = away + '_at_' + home
    main(home, away,year, week, output_gdb, output_fc)
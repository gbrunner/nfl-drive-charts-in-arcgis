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
footbal_field_fields = ('SHAPE@', 'TEAM')
footbal_line_fields = ('SHAPE@', 'MARKER')

def get_num_drives(drives):
    for drive in drives:
        drive_count = drive.drive_num

    return drive_count

def build_football_field(output_gdb, output_feature_class):
    print('Creating football field.')
    fc = os.path.join(output_gdb,output_feature_class)
    if not arcpy.Exists(os.path.join(output_gdb,output_feature_class)):
        arcpy.CreateFeatureclass_management(output_gdb,output_feature_class,"POLYGON","#","DISABLED","DISABLED", "PROJCS['WGS_1984_Web_Mercator_Auxiliary_Sphere',GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137.0,298.257223563]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Mercator_Auxiliary_Sphere'],PARAMETER['False_Easting',0.0],PARAMETER['False_Northing',0.0],PARAMETER['Central_Meridian',0.0],PARAMETER['Standard_Parallel_1',0.0],PARAMETER['Auxiliary_Sphere_Type',0.0],UNIT['Meter',1.0]]","#","0","0","0")
        arcpy.AddField_management(fc, footbal_field_fields[1],"TEXT", "", "", 20)

    cursor = arcpy.da.InsertCursor(fc,footbal_field_fields)

    field = arcpy.Array([arcpy.Point(0,533.3),
                     arcpy.Point(1000,533.3),
                     arcpy.Point(1000,0),
                     arcpy.Point(0,0)])
    field_polygon= arcpy.Polygon(field)
    cursor.insertRow([field_polygon, ""])

    home_endzone = arcpy.Array([arcpy.Point(-100,533.3),
                     arcpy.Point(0,533.3),
                     arcpy.Point(0,0),
                     arcpy.Point(-100,0)])
    field_polygon= arcpy.Polygon(home_endzone)
    cursor.insertRow([field_polygon, "SEATTLE"])

    away_endzone = arcpy.Array([arcpy.Point(1000,533.3),
                     arcpy.Point(1100,533.3),
                     arcpy.Point(1100,0),
                     arcpy.Point(1000,0)])
    field_polygon= arcpy.Polygon(away_endzone)
    cursor.insertRow([field_polygon, "NEW ENGLAND"])


def build_yard_lines(output_gdb, output_feature_class):
    print('Creating yard markers.')
    fc = os.path.join(output_gdb,output_feature_class)
    if not arcpy.Exists(os.path.join(output_gdb,output_feature_class)):
        arcpy.CreateFeatureclass_management(output_gdb,output_feature_class,"POLYLINE","#","DISABLED","DISABLED", "PROJCS['WGS_1984_Web_Mercator_Auxiliary_Sphere',GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137.0,298.257223563]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Mercator_Auxiliary_Sphere'],PARAMETER['False_Easting',0.0],PARAMETER['False_Northing',0.0],PARAMETER['Central_Meridian',0.0],PARAMETER['Standard_Parallel_1',0.0],PARAMETER['Auxiliary_Sphere_Type',0.0],UNIT['Meter',1.0]]","#","0","0","0")
        arcpy.AddField_management(fc, footbal_line_fields[1],"TEXT", "", "", 10)

    cursor = arcpy.da.InsertCursor(fc,footbal_line_fields)
    markers = [1,2,3,4,5,6,7,8,9]
    for marker in markers:
        line_1 = arcpy.Array([arcpy.Point(marker*100,533.3/2),
                     arcpy.Point(marker*100,0)])
        line_2 = arcpy.Array([arcpy.Point(marker*100,533.3/2),
                     arcpy.Point(marker*100,533.3)])
        field_line_1= arcpy.Polyline(line_1)
        field_line_2= arcpy.Polyline(line_2)
        if marker > 5:
            cursor.insertRow([field_line_1, str(10-marker)])
            cursor.insertRow([field_line_2, str(10-marker)])
        else:
            cursor.insertRow([field_line_1, str(marker)])
            cursor.insertRow([field_line_2, str(marker)])


def create_drive_feature_class(output_gdb, output_feature_class):
    feature_class = os.path.basename(output_feature_class)
    if not arcpy.Exists(output_gdb):
        arcpy.CreateFileGDB_management(os.path.dirname(output_gdb),os.path.basename(output_gdb))

    fc = os.path.join(output_gdb,output_feature_class)
    if not arcpy.Exists(os.path.join(output_gdb,output_feature_class)):
        #"PROJCS['WGS_1984_Web_Mercator_Auxiliary_Sphere',GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137.0,298.257223563]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Mercator_Auxiliary_Sphere'],PARAMETER['False_Easting',0.0],PARAMETER['False_Northing',0.0],PARAMETER['Central_Meridian',0.0],PARAMETER['Standard_Parallel_1',0.0],PARAMETER['Auxiliary_Sphere_Type',0.0],UNIT['Meter',1.0]]", transform_method="", in_coor_system="GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137.0,298.257223563]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]]"
        arcpy.CreateFeatureclass_management(output_gdb,output_feature_class,"POLYGON","#","DISABLED","DISABLED", "PROJCS['WGS_1984_Web_Mercator_Auxiliary_Sphere',GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137.0,298.257223563]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Mercator_Auxiliary_Sphere'],PARAMETER['False_Easting',0.0],PARAMETER['False_Northing',0.0],PARAMETER['Central_Meridian',0.0],PARAMETER['Standard_Parallel_1',0.0],PARAMETER['Auxiliary_Sphere_Type',0.0],UNIT['Meter',1.0]]","#","0","0","0")
        arcpy.AddField_management(fc, drive_fields[1],"TEXT", "", "", 10)
        arcpy.AddField_management(fc, drive_fields[2],"SHORT", "", "", "")
        arcpy.AddField_management(fc, drive_fields[3],"TEXT", "", "", 10)
        arcpy.AddField_management(fc, drive_fields[4],"TEXT", "", "", 10)
        arcpy.AddField_management(fc, drive_fields[5],"TEXT", "", "", 100)
        arcpy.AddField_management(fc, drive_fields[6],"TEXT", "", "", 100)
        arcpy.AddField_management(fc, drive_fields[7],"TEXT", "", "", 100)

def create_chart_polygon(drive, home, away):
    scale_by = 10
    #print(drive.field_start)
    #if drive.field_start:
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
    #else:
    #    return scale_by*50,scale_by*50.1

def get_game_drives(game):
    return [drive for drive in game.drives]

def get_drive_plays(drive):
    return [play for play in drive.plays]

def main(ome, away, year, week, reg_post, output_gdb, output_fc):
    game = nflgame.one(year, week, home,away, reg_post)

    print('Create drive feature class.')
    create_drive_feature_class(output_gdb, output_fc)

    print('Getting drive data.')
    drives = get_game_drives(game)
    drive_count = get_num_drives(drives)

    print('Opening insert cursor.')
    cursor = arcpy.da.InsertCursor(os.path.join(output_gdb, output_fc),drive_fields)

    drive_bar_height = 533.3/(drive_count)
    for drive in drives:
        if drive.field_start:
            start_x, end_x = create_chart_polygon(drive, home, away)
            if start_x==end_x:
                array = arcpy.Array([arcpy.Point(start_x, (drive.drive_num-1)*drive_bar_height),
                         arcpy.Point(end_x+0.1, (drive.drive_num-1)*drive_bar_height),
                         arcpy.Point(end_x+0.1, (drive.drive_num-1)*drive_bar_height+(drive_bar_height-1)),
                         arcpy.Point(start_x, (drive.drive_num-1)*drive_bar_height+(drive_bar_height-1))])
            else:
                array = arcpy.Array([arcpy.Point(start_x, (drive.drive_num-1)*drive_bar_height),
                         arcpy.Point(end_x, (drive.drive_num-1)*drive_bar_height),
                         arcpy.Point(end_x, (drive.drive_num-1)*drive_bar_height+(drive_bar_height-1)),
                         arcpy.Point(start_x, (drive.drive_num-1)*drive_bar_height+(drive_bar_height-1))])
            polygon= arcpy.Polygon(array)

            print(str(drive))
            cursor.insertRow([polygon, drive.team, drive.drive_num, str(drive.field_start),str(drive.field_end),str(drive.pos_time.__dict__['minutes']) + ' min and ' + str(drive.pos_time.__dict__['seconds']) + ' sec', drive.result, str(drive)])

    #print('Done.')


        #plays = get_drive_plays(drive)
        #for play in plays:
          #  print(play)
           # print(play.rushing_yds)
            #print(play.time)


if __name__ == '__main__':
    home = 'SEA'#'PIT'
    away = 'NE'#'DEN'
    year = 2014#2015
    week = 5#15
    reg_post = 'POST'
    output_gdb = "C:/NFL/superbowl_49.gdb"
    output_fc = away + '_at_' + home
    main(home, away,year, week, reg_post, output_gdb, output_fc)

    build_football_field(output_gdb, "field")
    build_yard_lines(output_gdb, "yard_lines")

    print('Done.')
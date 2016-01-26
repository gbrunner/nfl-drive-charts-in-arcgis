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
import arcpy

drive_fields = ('SHAPE@','TEAM','DRIVE_NUM','START_POS', 'END_POS', 'DURATION', 'RESULT', 'DESCRIPTION')
play_fields = ('SHAPE@', 'TEAM', 'DRIVE_NUM', 'START_POS', 'END_POS', 'DURATION', 'PLAY', 'RESULT', 'DESCRIPTION')
footbal_field_fields = ('SHAPE@', 'TEAM')
footbal_line_fields = ('SHAPE@', 'MARKER')

def get_num_drives(drives):
    for drive in drives:
        drive_count = drive.drive_num

    return drive_count

def get_num_plays(plays):
    for play in plays:
        play_count = play.play_num

    return play_count


def get_play_type(play):
    """
        Parses the play to determine the play type.
        Current solution is more-or-less brute force
        input:
            nflgame.play
        Returns:
            type of play [pass, rush, kick, fumble, penalty, sack, fg, touchdown, interception]
    """
    play_type = None
    play_result = None
    play_info = play.__dict__

    if "rushing_att" in play_info:
        play_type = "rush"
        play_result = play.rushing_yds
    if "passing_att" in play_info:
        play_type = "pass"
        play_result = play.passing_yds
    if "kicking_tot" in play_info:
        play_type = "kick"
        play_result = play.kicking_yds
    if "punting_tot" in play_info:
        play_type = "punt"
        play_result = play.punting_yds
    if "kicking_fga" in play_info:
        play_type = "field goal"
        if play_info.get("kicking_fgmissed", 0):
            play_type = play_type + " missed"
            play_result = 0
        else:
            play_type = play_type + "made"
            play_result = 0

    if "defense_sk_yds" in play_info:
        play_type = "sack"
        play_result = play.defense_sk_yds

    if "penalty" in play_info:
        play_type = "penalty"
        play_result = play.penalty_yds

    if "defense_int" in play_info:
        play_type = "interception"
        play_result = 0 #play.defense_int_yds

    if "timeout" in play_info:
        play_type = "timeout"

    if "touchdown" in play_info:
        if play_info["touchdown"]:
            play_type = str(play_type) + " touchdown"

    if "fumbles_tot" in play_info:
        if play_info.get('fumbles_lost', None):
            play_type = str(play_type) + " fumble lost"
        else:
            play_type = str(play_type) + " fumble recovered"

    if "kicking_xpa" in play_info:
        if play_info["kicking_xpmade"]:
            play_type = "extra point (1 point)"
        else:
            play_type = "extra point (FAILED)"

    if not play_type:
        print(play_info)
    if not play_result:
        print(play_info)

    return play_type, play_result

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

def create_play_feature_class(output_gdb, output_feature_class):
    feature_class = os.path.basename(output_feature_class)
    if not arcpy.Exists(output_gdb):
        arcpy.CreateFileGDB_management(os.path.dirname(output_gdb),os.path.basename(output_gdb))

    fc = os.path.join(output_gdb,output_feature_class)
    if not arcpy.Exists(os.path.join(output_gdb,output_feature_class)):
        #"PROJCS['WGS_1984_Web_Mercator_Auxiliary_Sphere',GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137.0,298.257223563]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Mercator_Auxiliary_Sphere'],PARAMETER['False_Easting',0.0],PARAMETER['False_Northing',0.0],PARAMETER['Central_Meridian',0.0],PARAMETER['Standard_Parallel_1',0.0],PARAMETER['Auxiliary_Sphere_Type',0.0],UNIT['Meter',1.0]]", transform_method="", in_coor_system="GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137.0,298.257223563]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]]"
        arcpy.CreateFeatureclass_management(output_gdb,output_feature_class,"POLYGON","#","DISABLED","DISABLED", "PROJCS['WGS_1984_Web_Mercator_Auxiliary_Sphere',GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137.0,298.257223563]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Mercator_Auxiliary_Sphere'],PARAMETER['False_Easting',0.0],PARAMETER['False_Northing',0.0],PARAMETER['Central_Meridian',0.0],PARAMETER['Standard_Parallel_1',0.0],PARAMETER['Auxiliary_Sphere_Type',0.0],UNIT['Meter',1.0]]","#","0","0","0")
        arcpy.AddField_management(fc, play_fields[1],"TEXT", "", "", 10)
        arcpy.AddField_management(fc, play_fields[2],"SHORT", "", "", "")
        arcpy.AddField_management(fc, play_fields[3],"TEXT", "", "", 10)
        arcpy.AddField_management(fc, play_fields[4],"TEXT", "", "", 10)
        arcpy.AddField_management(fc, play_fields[5],"TEXT", "", "", 100)
        arcpy.AddField_management(fc, play_fields[6],"TEXT", "", "", 100)
        arcpy.AddField_management(fc, play_fields[7],"TEXT", "", "", 100)
        arcpy.AddField_management(fc, play_fields[8],"TEXT", "", "", 1024)

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

def create_play_polygon(drive, play, yards, home, away):
    scale_by = 10
    #print(drive.field_start)
    #if drive.field_start:
    if drive.team == home:
        start_x = 50 + play.yardline.__dict__['offset']
        end_x = 50 + play.yardline.__dict__['offset']+yards

    if drive.team == away:
        start_x = 50 - play.yardline.__dict__['offset']
        end_x = 50 - play.yardline.__dict__['offset']-yards

    return scale_by*start_x,scale_by*end_x
    #else:
    #    return scale_by*50,scale_by*50.1

def get_game_drives(game):
    return [drive for drive in game.drives]

def get_drive_plays(drive):
    return [play for play in drive.plays]

def main(ome, away, year, week, reg_post, output_gdb, output_fc):
    game = nflgame.one(year, week, home,away, reg_post)

##    print('Create drive feature class.')
##    create_drive_feature_class(output_gdb, output_fc)

    print('Getting drive data.')
    drives = get_game_drives(game)
    drive_count = get_num_drives(drives)

##    print('Opening insert cursor.')
##    cursor = arcpy.da.InsertCursor(os.path.join(output_gdb, output_fc),drive_fields)
##
##    drive_bar_height = 533.3/(drive_count)
##    for drive in drives:
##        if drive.field_start:
##            start_x, end_x = create_chart_polygon(drive, home, away)
##            if start_x==end_x:
##                array = arcpy.Array([arcpy.Point(start_x, (drive.drive_num-1)*drive_bar_height),
##                         arcpy.Point(end_x+0.1, (drive.drive_num-1)*drive_bar_height),
##                         arcpy.Point(end_x+0.1, (drive.drive_num-1)*drive_bar_height+(drive_bar_height-1)),
##                         arcpy.Point(start_x, (drive.drive_num-1)*drive_bar_height+(drive_bar_height-1))])
##            else:
##                array = arcpy.Array([arcpy.Point(start_x, (drive.drive_num-1)*drive_bar_height),
##                         arcpy.Point(end_x, (drive.drive_num-1)*drive_bar_height),
##                         arcpy.Point(end_x, (drive.drive_num-1)*drive_bar_height+(drive_bar_height-1)),
##                         arcpy.Point(start_x, (drive.drive_num-1)*drive_bar_height+(drive_bar_height-1))])
##            polygon= arcpy.Polygon(array)
##
##            print(str(drive))
##            cursor.insertRow([polygon, drive.team, drive.drive_num, str(drive.field_start),str(drive.field_end),str(drive.pos_time.__dict__['minutes']) + ' min and ' + str(drive.pos_time.__dict__['seconds']) + ' sec', drive.result, str(drive)])

    #print('Done.')
    for drive in drives:
        if drive.field_start:
            plays = get_drive_plays(drive)
            print("Looking at drive " + str(drive.drive_num))
            create_play_feature_class(output_gdb, "drive_"+str(drive.drive_num))
            cursor = arcpy.da.InsertCursor(os.path.join(output_gdb, "drive_"+str(drive.drive_num)),play_fields)
            play_num = 1
            play_bar_height = 20
            for play in plays:
                #print(play)
                if play.yardline:
                    print(play.yardline)
                    print(play.time.__dict__)
                    play_type, yds = get_play_type(play)
                    if not yds:
                        yds = 0
                    start_x, end_x = create_play_polygon(drive, play, int(yds), home, away)
                    if int(yds)==0:
                        array = arcpy.Array([arcpy.Point(start_x, (play_num-1)*play_bar_height),
                             arcpy.Point(end_x+0.1, (play_num-1)*play_bar_height),
                             arcpy.Point(end_x+0.1, (play_num-1)*play_bar_height+(play_bar_height-1)),
                             arcpy.Point(start_x, (play_num-1)*play_bar_height+(play_bar_height-1))])
                    else:
                        array = arcpy.Array([arcpy.Point(start_x, (play_num-1)*play_bar_height),
                             arcpy.Point(end_x, (play_num-1)*play_bar_height),
                             arcpy.Point(end_x, (play_num-1)*play_bar_height+(play_bar_height-1)),
                             arcpy.Point(start_x, (play_num-1)*play_bar_height+(play_bar_height-1))])
                    polygon= arcpy.Polygon(array)
                    print(str(play))
                    if (play_type != "punt") or (play_type!="kick"):
                        cursor.insertRow([polygon, drive.team, drive.drive_num, str(play.yardline),"",str(play.time), play_type, yds, str(play)])
                        play_num=play_num+1


if __name__ == '__main__':
    home = 'SEA'#'PIT'
    away = 'NE'#'DEN'
    year = 2014#2015
    week = 5#15
    reg_post = 'POST'
    output_gdb = "C:/NFL/superbowl_49_test6.gdb"
    output_fc = away + '_at_' + home
    main(home, away,year, week, reg_post, output_gdb, output_fc)

    #build_football_field(output_gdb, "field")
    #build_yard_lines(output_gdb, "yard_lines")

    print('Done.')
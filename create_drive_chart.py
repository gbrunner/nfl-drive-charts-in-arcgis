"""----------------------------------------------------------------------------
 Name:        create_drive_chart.py
 Purpose:

 Author:      Gregory Brunner, Esri

 Created:     14/01/2016
 Copyright:   (c) greg6750 2016
 Licence:     <your licence>
----------------------------------------------------------------------------"""

import os
import nflgame
import arcpy

drive_fields = ('SHAPE@', 'TEAM', 'DRIVE_NUM', 'START_POS', 'END_POS',
                'DURATION', 'RESULT', 'DESCRIPTION')
play_fields = ('SHAPE@', 'TEAM', 'DRIVE_NUM', 'START_POS', 'END_POS',
               'DURATION', 'PLAY', 'RESULT', 'DESCRIPTION')
footbal_field_fields = ('SHAPE@', 'TEAM')
footbal_line_fields = ('SHAPE@', 'MARKER')


def get_num_drives(drives):
    for drive in drives:
        drive_count = drive.drive_num

    return drive_count


def get_num_plays(plays):
    play_count = 0
    for play in plays:
        play_count += 1

    return play_count


def get_play_type(play):
    play_type = None
    play_result = None
    play_info = play.__dict__

    if "rushing_att" in play_info:
        play_type = "Rush"
        play_result = play.rushing_yds
    if "passing_att" in play_info:
        play_type = "Pass"
        play_result = play.passing_yds
    if "kicking_tot" in play_info:
        play_type = "Kick"
        play_result = play.kicking_yds
    if "punting_tot" in play_info:
        play_type = "Punt"
        play_result = play.punting_yds
    if "kicking_fga" in play_info:
        play_type = "Field Goal"
        if play_info.get("kicking_fgmissed", 0):
            play_type += " Missed"
            play_result = 0
        else:
            play_type += " Made"
            play_result = 0

    if "defense_sk_yds" in play_info:
        play_type = "Sack"
        play_result = play.defense_sk_yds

    if "penalty" in play_info:
        play_type = "Penalty"
        play_result = -play.penalty_yds

    if "defense_int" in play_info:
        play_type = "Interception"
        play_result = 0  # play.defense_int_yds

    if "timeout" in play_info:
        play_type = "Timeout"

    if "touchdown" in play_info:
        if play_info["touchdown"]:
            play_type = str(play_type) + " Touchdown"

    if "fumbles_tot" in play_info:
        if play_info.get('fumbles_lost', None):
            play_type = str(play_type) + " Fumble Lost"
        else:
            play_type = str(play_type) + " Fumble Recovered"

    if "kicking_xpa" in play_info:
        if play_info["kicking_xpmade"]:
            play_type = "Extra Point (GOOD)"
        else:
            play_type = "Extra Point (FAILED)"

    if not play_type:
        print(play_info)
    if not play_result:
        print(play_info)

    return play_type, play_result


def build_football_field(output_gdb, output_feature_class):
    print('Creating football field.')
    fc = os.path.join(output_gdb, output_feature_class)
    if not arcpy.Exists(os.path.join(output_gdb, output_feature_class)):
        arcpy.CreateFeatureclass_management(
            output_gdb, output_feature_class, "POLYGON", "#", "DISABLED",
            "DISABLED", arcpy.SpatialReference(3857))
        arcpy.AddField_management(fc, footbal_field_fields[1], "TEXT",
                                  field_length=20)

    cursor = arcpy.da.InsertCursor(fc, footbal_field_fields)

    field = [(0, 533.3),
             (1000, 533.3),
             (1000, 0),
             (0, 0)]
    cursor.insertRow([field, ""])

    home_endzone = [(-100, 533.3),
                    (0, 533.3),
                    (0, 0),
                    (-100, 0)]
    cursor.insertRow([home_endzone, "SEATTLE"])

    away_endzone = [(1000, 533.3),
                    (1100, 533.3),
                    (1100, 0),
                    (1000, 0)]
    cursor.insertRow([away_endzone, "NEW ENGLAND"])


def build_yard_lines(output_gdb, output_feature_class):
    print('Creating yard markers.')
    fc = os.path.join(output_gdb, output_feature_class)
    if not arcpy.Exists(os.path.join(output_gdb, output_feature_class)):
        arcpy.CreateFeatureclass_management(
            output_gdb, output_feature_class, "POLYLINE", "#", "DISABLED",
            "DISABLED", arcpy.SpatialReference(3857))
        arcpy.AddField_management(fc, footbal_line_fields[1], "TEXT",
                                  field_length=10)

    cursor = arcpy.da.InsertCursor(fc, footbal_line_fields)
    markers = [10, 20, 30, 40, 50, 60, 70, 80, 90]
    for marker in markers:
        line_1 = [(marker * 10, 533.3 / 2), (marker * 10, 0)]
        line_2 = [(marker * 10, 533.3 / 2), (marker * 10, 533.3)]
        if marker > 50:
            cursor.insertRow([line_1, str(100 - marker)])
            cursor.insertRow([line_2, str(100 - marker)])
        else:
            cursor.insertRow([line_1, str(marker)])
            cursor.insertRow([line_2, str(marker)])


def create_drive_feature_class(output_gdb, output_feature_class):
    feature_class = os.path.basename(output_feature_class)
    if not arcpy.Exists(output_gdb):
        arcpy.CreateFileGDB_management(os.path.dirname(output_gdb),
                                       os.path.basename(output_gdb))

    fc = os.path.join(output_gdb, output_feature_class)
    if not arcpy.Exists(os.path.join(output_gdb, output_feature_class)):
        arcpy.CreateFeatureclass_management(
            output_gdb, output_feature_class, "POLYGON", "#", "DISABLED",
            "DISABLED", arcpy.SpatialReference(3857))
        arcpy.AddField_management(fc, drive_fields[1], "TEXT", field_length=10)
        arcpy.AddField_management(fc, drive_fields[2], "SHORT")
        arcpy.AddField_management(fc, drive_fields[3], "TEXT", field_length=10)
        arcpy.AddField_management(fc, drive_fields[4], "TEXT", field_length=10)
        arcpy.AddField_management(fc, drive_fields[5], "TEXT", field_length=100)
        arcpy.AddField_management(fc, drive_fields[6], "TEXT", field_length=100)
        arcpy.AddField_management(fc, drive_fields[7], "TEXT", field_length=100)


def create_play_feature_class(output_gdb, output_feature_class):
    feature_class = os.path.basename(output_feature_class)
    if not arcpy.Exists(output_gdb):
        arcpy.CreateFileGDB_management(os.path.dirname(output_gdb),
                                       os.path.basename(output_gdb))

    fc = os.path.join(output_gdb, output_feature_class)
    if not arcpy.Exists(os.path.join(output_gdb, output_feature_class)):
        arcpy.CreateFeatureclass_management(
            output_gdb, output_feature_class, "POLYGON", "#", "DISABLED",
            "DISABLED", arcpy.SpatialReference(3857))
        arcpy.AddField_management(fc, play_fields[1], "TEXT", field_length=10)
        arcpy.AddField_management(fc, play_fields[2], "SHORT")
        arcpy.AddField_management(fc, play_fields[3], "TEXT", field_length=10)
        arcpy.AddField_management(fc, play_fields[4], "TEXT", field_length=10)
        arcpy.AddField_management(fc, play_fields[5], "TEXT", field_length=100)
        arcpy.AddField_management(fc, play_fields[6], "TEXT", field_length=100)
        arcpy.AddField_management(fc, play_fields[7], "TEXT", field_length=100)
        arcpy.AddField_management(fc, play_fields[8], "TEXT", field_length=1024)


def create_chart_polygon(drive, home, away):
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

    return scale_by * start_x, scale_by * end_x


def create_play_polygon(drive, play, yards, home, away):
    scale_by = 10
    if drive.team == home:
        start_x = 50 + play.yardline.__dict__['offset']
        end_x = 50 + play.yardline.__dict__['offset'] + yards

    if drive.team == away:
        start_x = 50 - play.yardline.__dict__['offset']
        end_x = 50 - play.yardline.__dict__['offset'] - yards

    return scale_by * start_x, scale_by * end_x


def get_game_drives(game):
    return [drive for drive in game.drives]


def get_drive_plays(drive):
    return [play for play in drive.plays]


def main(home, away, year, week, reg_post, output_gdb, output_fc):
    print('Create drive feature class.')
    create_drive_feature_class(output_gdb, output_fc)

    print('Getting game data.')
    game = nflgame.one(year, week, home, away, reg_post)

    print('Getting drive data.')
    drives = get_game_drives(game)
    drive_count = get_num_drives(drives)

    print('Opening insert cursor.')
    cursor = arcpy.da.InsertCursor(os.path.join(output_gdb, output_fc),
                                   drive_fields)

    drive_bar_height = 533.3 / drive_count
    for drive in drives:
        if drive.field_start:
            start_x, end_x = create_chart_polygon(drive, home, away)
            if start_x == end_x:
                polygon = [
                    (start_x, (drive_count - drive.drive_num) * drive_bar_height),
                    (end_x + 0.1, (drive_count - drive.drive_num) * drive_bar_height),
                    (end_x + 0.1, (drive_count - drive.drive_num) * drive_bar_height + (drive_bar_height - 1)),
                    (start_x, (drive_count - drive.drive_num) * drive_bar_height + (drive_bar_height - 1))]
            else:
                polygon = [
                    (start_x, (drive_count - drive.drive_num) * drive_bar_height),
                    (end_x, (drive_count - drive.drive_num) * drive_bar_height),
                    (end_x, (drive_count - drive.drive_num) * drive_bar_height + (drive_bar_height - 1)),
                    (start_x, (drive_count - drive.drive_num) * drive_bar_height + (drive_bar_height - 1))]

            print(str(drive))
            cursor.insertRow([polygon, drive.team, drive.drive_num,
                              str(drive.field_start), str(drive.field_end),
                              str(drive.pos_time.__dict__['minutes']) + ' min and ' +
                              str(drive.pos_time.__dict__['seconds']) + ' sec',
                              drive.result, str(drive)])

    for drive in drives:
        if drive.field_start:
            if drive.drive_num > 0:
                plays = get_drive_plays(drive)
                play_count = get_num_plays(plays)
                print("Looking at drive " + str(drive.drive_num))
                create_play_feature_class(output_gdb,
                                          "drive_" + str(drive.drive_num))
                cursor = arcpy.da.InsertCursor(
                    os.path.join(output_gdb, "drive_" + str(drive.drive_num)),
                    play_fields)
                play_num = 1
                play_bar_height = 30  # (533.3/2)/(play_count)
                initial_y = (play_count / 2) * play_bar_height + (533.3 / 2)
                for play in plays:
                    if play.yardline:
                        play_type, yds = get_play_type(play)
                        if not yds:
                            yds = 0
                        start_x, end_x = create_play_polygon(drive, play, int(yds), home, away)
                        if int(yds) == 0:
                            polygon = [
                                (start_x, initial_y - (play_num - 1) * play_bar_height),
                                (end_x + 0.1, initial_y - (play_num - 1) * play_bar_height),
                                (end_x + 0.1, initial_y - (play_num - 1) * play_bar_height - (play_bar_height - 1)),
                                (start_x, initial_y - (play_num - 1) * play_bar_height - (play_bar_height - 1))]
                        else:
                            polygon = [
                                (start_x, initial_y - (play_num - 1) * play_bar_height),
                                (end_x, initial_y - (play_num - 1) * play_bar_height),
                                (end_x, initial_y - (play_num - 1) * play_bar_height - (play_bar_height - 1)),
                                (start_x, initial_y - (play_num - 1) * play_bar_height - (play_bar_height - 1))]

                        # print(str(play))
                        if (play_type != "Punt") and (play_type != "Kick"):
                            print(play_type)
                            cursor.insertRow(
                                [polygon, drive.team, drive.drive_num, str(play.yardline), "", str(play.time),
                                 play_type, yds, str(play)])
                            play_num += 1


if __name__ == '__main__':
    home = 'SEA'  # 'PIT'
    away = 'NE'  # 'DEN'
    year = 2014  # 2015
    week = 5  # 15
    reg_post = 'POST'  # 'REG'
    output_gdb = "C:/PROJECTS/R&D/NFL/superbowl_xlix.gdb"
    output_fc = away + '_at_' + home
    main(home, away, year, week, reg_post, output_gdb, output_fc)

    build_football_field(output_gdb, "field")
    build_yard_lines(output_gdb, "yard_lines")

    print('Done.')

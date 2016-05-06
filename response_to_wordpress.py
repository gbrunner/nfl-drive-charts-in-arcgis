import os
import nflgame
import arcpy


def build_football_field(final,footballfield): # function called build_football_field (output_gdb, output_feature_class):
    print('Creating football field.')
    football_field_fields = ('SHAPE@', 'TEAM')
    fc = os.path.join(final,footballfield) # fc = joining the paths of final.gdb and footballfield (output gdb, outputfeatureclass)
    if not arcpy.Exists(os.path.join(final, footballfield)): #checking to see if path exists
        arcpy.CreateFeatureclass_management(final, footballfield, "POLYGON", "#","DISABLED","DISABLED", arcpy.SpatialReference(3857)) #creates a polygon feature class in final.gdb with spatial reference of WGS 1984 Web Mercator
        arcpy.AddField_management(fc, football_field_fields[1], "TEXT",field_length=20) #adds a new field to the table

    cursor = arcpy.da.InsertCursor(fc, football_field_fields) #inserting a row into the table (in_table, field_names)

    field = [(0, 533.3), #vertices of the field
        (1000, 533.3),
        (1000, 0),
        (0, 0)]
    cursor.insertRow([field,""]) #inserting row

    home_endzone = [(-100, 533.3), #vertices of the home endzone
        (0, 533.3),
        (0, 0),
        (-100, 0)]
    cursor.insertRow([home_endzone, "Packers"]) #inserting row for home_endzone called Packers

    away_endzone = [(1000, 533.3), #vertices of away_endzone
        (1100, 533.3),
        (1100, 0),
        (1000, 0)]
    cursor.insertRow([away_endzone, "Bears"]) #inserting row for away_endzone called Bears

    #need to call the function

    #Function 2:

def build_yard_lines(final,yardlines): #function called build_yard_lines (output_gdb, output_feature_class):
    print('Creating yard markers.')
    football_line_fields = ('SHAPE@', 'MARKER') # creating an object (shape@, marker)
    fc = os.path.join(final, yardlines) # joining paths of yardlines and final.gdb(ouput_gdb, output_feature_class)
    if not arcpy.Exists(os.path.join(final, yardlines)): #checking to see if path exists
        arcpy.CreateFeatureclass_management(final, yardlines, "POLYLINE", "#", "DISABLED","DISABLED", arcpy.SpatialReference(3857))
    #creates a polyline feature class in final.gdb with spatial reference of WGS 1984 Web Mercator
        arcpy.AddField_management(fc, football_line_fields[1], "TEXT",field_length=10) #adding new field to the table

    cursor = arcpy.da.InsertCursor(fc, football_line_fields) #inserting a row into the table (in_table, field_names)
    markers = [10, 20, 30, 40, 50, 60, 70, 80, 90] #creating markers
    for marker in markers:
        line_1 = [(marker * 10, 533.3 / 2), (marker * 10, 0)]
        line_2 = [(marker * 10, 533.3 / 2), (marker * 10, 533.3)]
        if marker > 50:
            cursor.insertRow([line_1, str(100 - marker)])
            cursor.insertRow([line_2, str(100 - marker)])
        else:
            cursor.insertRow([line_1, str(marker)])
            cursor.insertRow([line_2, str(marker)])

if __name__ == '__main__':
    arcpy.CreateFileGDB_management("C:\\Users\\greg\\Desktop\\Python", "final.gdb")
    field1 = build_football_field("C:\\Users\\greg\\Desktop\\Python\\final.gdb", "footballfield")
    lines = build_yard_lines("C:\\Users\\greg\\Desktop\\Python\\final.gdb","yardlines")
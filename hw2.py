import os
import sys


EXPECTED_VALUES_PER_LINE = 3  # every building line needs height, left x, and right x


def read_input_file(input_path):
    
    buildings = []  # all valid building records go here

    input_file = open(input_path, "r")  # open input file for reading

    line_number = 0  # helps explain which input line has a problem

    for line in input_file:
        
        line_number = line_number + 1  # move to current line number
        line = line.strip()  # remove outside spaces and newline

        if line == "":  # blank lines do not describe a building
            continue

        line_parts = line.split(",")  # split comma separated values

        for index in range(len(line_parts)):  # clean each value after split
            line_parts[index] = line_parts[index].strip()

        if len(line_parts) != EXPECTED_VALUES_PER_LINE:  # building must have exactly three values
            input_file.close()
            raise ValueError("Line " + str(line_number) + " must have height, left x, and right x.")

        try:
            building_height = int(line_parts[0])  # first value is building height
            left_x = int(line_parts[1])  # second value is left x-coordinate
            right_x = int(line_parts[2])  # third value is right x-coordinate
        except ValueError:
            input_file.close()
            raise ValueError("Line " + str(line_number) + " must contain integers only.")

        if building_height < 0:  # height cannot be negative
            input_file.close()
            raise ValueError("Line " + str(line_number) + " has a negative building height.")

        if left_x < 0 or right_x < 0:  # coordinates cannot be negative
            input_file.close()
            raise ValueError("Line " + str(line_number) + " has a negative x-coordinate.")

        if left_x >= right_x:  # building must have actual width
            input_file.close()
            raise ValueError("Line " + str(line_number) + " must have left x smaller than right x.")

        building = (building_height, left_x, right_x)  # use assignment order for one building
        buildings.append(building)  # save building for algorithm

    input_file.close()  # close input file

    buildings.sort(key=lambda building: (building[1], building[2], building[0]))  # left to right order

    return buildings  # output contract: list of building tuples


def add_skyline_strip(skyline, strip_height, strip_x):
    
    # keeps one useful strip for each visible skyline change

    if len(skyline) == 0:  # first strip can be added directly
        skyline.append((strip_height, strip_x))
        return

    last_height = skyline[-1][0]  # height of last saved strip
    last_x = skyline[-1][1]  # x-coordinate of last saved strip

    if last_x == strip_x:  # two skyline changes happened at same x-coordinate
        higher_height = max(last_height, strip_height)  # visible shape uses higher height
        skyline[-1] = (higher_height, strip_x)  # keep only one strip at this x-coordinate

        if len(skyline) > 1 and skyline[-2][0] == skyline[-1][0]:  # same height as strip before it
            skyline.pop()  # newest strip did not create a visible change

        return

    if last_height == strip_height:  # same height means no new skyline corner
        return

    skyline.append((strip_height, strip_x))  # save real height change


def merge_skylines(left_skyline, right_skyline):
    
    merged_skyline = []  # final result made from both smaller skylines

    left_index = 0  # current location in left skyline
    right_index = 0  # current location in right skyline

    left_height = 0  # visible left skyline height at current x
    right_height = 0  # visible right skyline height at current x

    while left_index < len(left_skyline) and right_index < len(right_skyline):
        
        left_strip_height = left_skyline[left_index][0]  # current left height change
        left_strip_x = left_skyline[left_index][1]  # current left x-coordinate

        right_strip_height = right_skyline[right_index][0]  # current right height change
        right_strip_x = right_skyline[right_index][1]  # current right x-coordinate

        if left_strip_x < right_strip_x:
            current_x = left_strip_x  # next change comes from left skyline
            left_height = left_strip_height  # update left visible height
            left_index = left_index + 1  # move left skyline forward

        elif right_strip_x < left_strip_x:
            current_x = right_strip_x  # next change comes from right skyline
            right_height = right_strip_height  # update right visible height
            right_index = right_index + 1  # move right skyline forward

        else:
            current_x = left_strip_x  # both skylines change at same x-coordinate
            left_height = left_strip_height  # update left visible height
            right_height = right_strip_height  # update right visible height
            left_index = left_index + 1  # move left skyline forward
            right_index = right_index + 1  # move right skyline forward

        visible_height = max(left_height, right_height)  # outer shape uses taller side
        add_skyline_strip(merged_skyline, visible_height, current_x)  # add only real skyline change

    while left_index < len(left_skyline):
        
        left_height = left_skyline[left_index][0]  # next remaining left height
        current_x = left_skyline[left_index][1]  # next remaining left x-coordinate
        visible_height = max(left_height, right_height)  # right side may still affect height

        add_skyline_strip(merged_skyline, visible_height, current_x)  # save visible change
        left_index = left_index + 1  # move left skyline forward

    while right_index < len(right_skyline):
        
        right_height = right_skyline[right_index][0]  # next remaining right height
        current_x = right_skyline[right_index][1]  # next remaining right x-coordinate
        visible_height = max(left_height, right_height)  # left side may still affect height

        add_skyline_strip(merged_skyline, visible_height, current_x)  # save visible change
        right_index = right_index + 1  # move right skyline forward

    return merged_skyline  # output contract: merged skyline strips


def find_skyline(buildings):
    
    building_count = len(buildings)  # number of buildings in this smaller problem

    if building_count == 0:  # no buildings means no skyline
        return []

    if building_count == 1:
        building_height = buildings[0][0]  # one building height
        left_x = buildings[0][1]  # one building left side
        right_x = buildings[0][2]  # one building right side

        if building_height == 0:  # zero height does not rise above ground
            return []

        return [(building_height, left_x), (0, right_x)]  # building starts then returns to ground

    middle_index = building_count // 2  # divide buildings into two smaller groups

    left_buildings = buildings[:middle_index]  # left half of buildings
    right_buildings = buildings[middle_index:]  # right half of buildings

    left_skyline = find_skyline(left_buildings)  # recursively solve left half
    right_skyline = find_skyline(right_buildings)  # recursively solve right half

    return merge_skylines(left_skyline, right_skyline)  # combine both answers


def write_output_file(output_path, skyline):
    
    output_file = open(output_path, "w")  # open output file for writing

    for strip_height, strip_x in skyline:
        output_file.write(str(strip_height) + ", " + str(strip_x) + "\n")  # assignment output format

    output_file.close()  # close output file


def main():
    # input contract: command needs input path and output path

    if len(sys.argv) != 3:
        print("Usage: python assignment2.py <absolute input path> <absolute output path>")
        return

    input_path = os.path.abspath(sys.argv[1])  # convert given input path to absolute path
    output_path = os.path.abspath(sys.argv[2])  # convert given output path to absolute path

    try:
        buildings = read_input_file(input_path)  # read and validate buildings
        skyline = find_skyline(buildings)  # run O(n log n) divide-and-conquer algorithm
        write_output_file(output_path, skyline)  # save required output format

    except FileNotFoundError:
        print("Error: The input file was not found.")

    except PermissionError:
        print("Error: The program does not have permission to use one of the files.")

    except ValueError as error_message:
        print("Error: " + str(error_message))

    except OSError as error_message:
        print("Error: " + str(error_message))


main()

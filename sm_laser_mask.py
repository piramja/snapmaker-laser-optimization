# @author: Keivan (www.piramja.de) / Facebook: https://www.facebook.com/piramja/
#
# @descr: This script parses g-code files generated by Snapmaker Luban for laser engraving line-filled
#         grayscale images and changes all working movements that have laser output below the threshold value
#         to jogging movements, thus resulting in much higher engraving speed (depending on the image and the
#         threshold of course.. and your given jogging speed)
#
# @license: Public domain. Do with this script whatever you want, be free! But don't hold me responsible,
#           it comes as is without any warranty!
#
# @usage: It's pretty straight forward. You create your design in Luban, export your g-code file in the workspace tab.
#         Then open the command line (cmd in Windows, python has to be installed and put in the PATH variable) and run:
#
#         python sm_laser_mask.py your_gcode_file.nc output_gcode_file.nc 50
#
#         where 50 is the threshold value and should be between 1 and 255. I had great results with a value of 50 so far but
#         feel free to play around.
#
#         Then you can just import the generated .nc file back into Luban. That's it!
#         Just notice that the processing time that Luban shows will not be changed, because it's calculated during generation
#         and this script doesn't recalculate it. Let yourself be surprised how fast it will be (;
#
# PLEASE MAKE SURE YOU KNOW WHAT YOU ARE DOING! I strongly recommend to test the output of this script with a
# g-code simulation software (CAMotics for example) to make sure it does what you expect. And have fun (:

import re
import sys

# Check if enough arguments are provided
if len(sys.argv) != 4:
    print("Usage: python sm_laser_mask.py <input_filename> <output_filename> <threshold_value>")
    sys.exit(1)

# Assign command line arguments to variables
input_file_path = sys.argv[1]
output_file_path = sys.argv[2]
threshold_value = float(sys.argv[3])

# Compile the regular expression for matching lines
regex = re.compile(r'G1(.*?)S((?:\d{1,2}(?:\.\d+)?|0)(?=\D|$))\s')

# Initialize a counter for the number of changed lines
changed_lines_count = 0

# Function to check if a line should be replaced and to count the changed lines
def replace_line(match):
    x_value = float(match.group(2))
    if x_value < threshold_value:
        global changed_lines_count
        changed_lines_count += 1
        return f'G0{match.group(1)}S0\n'
    else:
        return match.group(0)

# Function to determine if a G0 command should be retained
def is_essential_g0_command(line):
    return "F" in line or "Y" in line

# Open the input file and read line by line
with open(input_file_path, 'r') as input_file, open(output_file_path, 'w') as output_file:
    previous_line = None
    for line in input_file:
        # Check if the line matches the regex and replace if necessary
        new_line = regex.sub(replace_line, line)

        # If the previous line and the current line are both "G0" commands, and the previous line is not essential, skip writing the previous line
        if previous_line and previous_line.startswith("G0") and new_line.startswith("G0") and not is_essential_g0_command(previous_line):
            previous_line = new_line  # Replace the previous line with the current one
        else:
            # If there's a previous line stored, write it to the file
            if previous_line:
                output_file.write(previous_line)
            previous_line = new_line  # Store the current line as the previous line

    # Write the last stored line to the file
    if previous_line:
        output_file.write(previous_line)

print(f'Processed lines have been saved to {output_file_path}.')
print(f'Total number of changed lines: {changed_lines_count}')

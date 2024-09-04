import numpy as np
import sys
import random
import functools as ft
import argparse

"""edit_manning.py

USAGE:
    $ python rand_manning.py <fort13> <fort14>

where fort13 and fort14 are the names of fort.13 and fort.14 files.
The output is written to a new file fort13.modified.
Requires numpy >= 1.16.0.

"""
#############################################################
# Main program

# Box to randomize manning's n
xmin = -95.5
xmax = -94.
ymin = 28.5
ymax = 30.

def main():
    parser = argparse.ArgumentParser(
        prog='Manning\'s n editor',
        description='What the program does',
        epilog='Text at the bottom of help')

    parser.add_argument('fort13', type=str)
    parser.add_argument('fort14', type=str)
    parser.add_argument('--criteria', type=int,
                        help='(1) = Galveston bay area, (2) = Galveston bay area AND above NAVD level',
                        default=1, dest='criterion', choices=range(1,3))
    parser.add_argument('--modifier', type=int,
                        help='(1) = Randomize mannings n between 0.02 and 0.2, (2) = Multiply by FACTOR',
                        default=1, dest='modifier', choices=range(1,3))
    parser.add_argument('--factor', type=float, help='Factor to multiply if modifier 2 is chosen',
                        default=5., dest='factor')
    parser.add_argument('-o', type=str, help='Output file name. If not specified, will be <fort13>.modified', dest='outfile')

    args = parser.parse_args()
    fort13 = args.fort13
    fort14 = args.fort14

    arr14 = load14(fort14)

    if args.outfile is not None:
      outfile = args.outfile
    else:
      outfile = fort13 + '.modified'

    if args.criterion == 1:
        criterion = is_node_in_box
    else:
        criterion = lambda node,f14 : is_node_in_box(node,f14) and is_node_above_navd(node,f14)

    if args.modifier == 1:
        modifier = randomize_mannings
    else:
        modifier = ft.partial(multiply_mannings, factor=args.factor)

    modify_count = write13(fort13, outfile, arr14, criterion, modifier)
    print("Modified " + str(modify_count) + " nodes.")


#############################################################
# Functions

# Load fort.14 into memory to access x and y coordinates for each node
def load14(fname):
    # Get the number of nodes
    with open(fname) as f:
        l1 = f.readline()
        l1 = f.readline()
        l1 = l1.split()
        NP = int(l1[1])
        print("NP = %d" %NP)

    arr = np.loadtxt(fname, skiprows=2, usecols=(1,2,3), max_rows=NP)
    return arr



#############################################################
# Different ways to modify the manning's n

def multiply_mannings(old_mannings, factor):
    return factor*old_mannings

def randomize_mannings(old_mannings):
    return random.uniform(0.02, 0.2)

#############################################################
# Different criteria for picking a node to be modified

# check if a node lies inside the box
def is_node_in_box(node, arr):
    x = arr[node-1, 0]
    y = arr[node-1, 1]
    return ((x <= xmax and x >= xmin) and (y <= ymax and y >= ymin))

def is_node_above_navd(node, arr, navd=0.276):
    bath = -arr[node-1, 2]
    return (bath >= navd)

#############################################################

# Load and copy fort.13 with edited section
def write13(fort13, fort13_out, arr14, criteria, modifier):
    with open(fort13, 'r') as f1, open(fort13_out, "w") as f2:

        # Read until first "manning's n" keyword
        wflg = False
        while True:
            line = f1.readline()
            lines = line.split()
            f2.write(line)
            if lines[0] == "mannings_n_at_sea_floor":
                if not wflg:
                    wflg = True
                else:
                    break

        # Randomize the manning's n
        l = f1.readline()
        mannings_node = int(l.split()[0])
        f2.write(l)


        modify_count = 0
        for i in range(mannings_node):
            line = f1.readline()
            lines = line.split()

            # if node in box, randomize the friction
            node = int(lines[0])
            old_mannings = float(lines[1])

            if criteria(node, arr14):
                new_mannings = modifier(old_mannings)
                f2.write("%d %.6f\n" % (node, new_mannings))

                modify_count += 1

            else:
                f2.write(line)

        print("Finished.")

        # Copy the rest of the file
        while True:
            line = f1.readline()
            if not line:
                break

            f2.write(line)

        # Print how many nodes were randomized
        return modify_count


# check number of edits
def count_diff():
    count = 0
    with open(fort13, 'r') as f1, open("fort.13.modified", "r") as f2:
        while True:
            l1 = f1.readline()
            l2 = f2.readline()
            if (not l1) or (not l2):
                break
            if not l1 == l2:
                count += 1


    return count


if __name__ == "__main__":
    main()

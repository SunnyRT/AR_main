#!/usr/bin/env python3
"""Parse command line options and arguments for the Logic Simulator.

This script parses options and arguments specified on the command line, and
runs either the command line user interface or the graphical user interface.

Usage
-----
Show help: logsim.py -h
Command line user interface: logsim.py -c <file path>
Graphical user interface: logsim.py <file path>
"""
import getopt
import sys

import wx

from gui import Gui


def main(arg_list):
    """Parse the command line options and arguments specified in arg_list.

    Run either the command line user interface, the graphical user interface,
    or display the usage message.
    """
    usage_message = ("Usage:\n"
                     "Show help: logsim.py -h\n"
                     "Command line user interface: logsim.py -c <file path>\n"
                     "Graphical user interface: logsim.py <file path>")
    try:
        options, arguments = getopt.getopt(arg_list, "hc:")
    except getopt.GetoptError:
        print("Error: invalid command line arguments\n")
        print(usage_message)
        sys.exit()

    # Initialise instances of the four inner simulator classes
    # names = Names()
    # devices = Devices(names)
    # network = Network(names, devices)
    # monitors = Monitors(names, devices, network)
    # names = None
    # devices = None
    # network = None
    # monitors = None


    for option, _ in options:
        if option == "-h":  # print the usage message
            print(usage_message)
            sys.exit()
        # elif option == "-c":  # use the command line user interface
        #     scanner = Scanner(path, names)
        #     parser = Parser(names, devices, network, monitors, scanner)
        #     if parser.parse_network():
        #         # Initialise an instance of the userint.UserInterface() class
        #         userint = UserInterface(names, devices, network, monitors)
        #         userint.command_interface()

    if not options:  # no option given, use the graphical user interface

        if len(arguments) != 2:  # wrong number of arguments
            print("Error: two file path required, one for 3d ply mesh, one for 2d image.\n")
            print(usage_message)
            sys.exit()

        mesh_file = arguments[0]
        image_file = arguments[1]
        # mesh_file = "D:\\sunny\\Codes\\IIB_project\\data\\summer\\fitted_otic_capsule.ply"
        # image_file = "D:\\sunny\\Codes\\IIB_project\\data\\summer\\JPEG1187.jpg"


        app = wx.App()
        gui = Gui("3D Model and 2D Image Display", mesh_file, image_file)
        # gui = Gui('Logic Simulator', "PATH", "names", "devices", "network", "monitors")
        gui.Show(True)
        app.MainLoop()


if __name__ == "__main__":
    main(sys.argv[1:])

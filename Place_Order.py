# import time #I dont think i use this anyway
import tkinter as tk  # Imports tk widgets
# Imports tkk widgets (From my understanding it just got some other configuration possibilities than tk)
import tkinter.ttk as ttk
from tkinter.constants import DISABLED, HORIZONTAL, NORMAL, NSEW
from typing import Dict
from robodk import robodk
from robolink import robolink
import time
from math import pi

import threading

# Establish the link between RoboDK and Python
rdk = robolink.Robolink()

# Retrieve the robot.
robot = rdk.Item("Fanuc LR Mate 200iD", itemtype=robolink.ITEM_TYPE_ROBOT)

# Retrieve all frames and targets from RoboDK
allFrames = rdk.ItemList(filter=robolink.ITEM_TYPE_FRAME)
allTargets = rdk.ItemList(filter=robolink.ITEM_TYPE_TARGET)

# Declare new containers for the correct frames and targets
correctCoverFrames = []
correctCoverTargets = []

# Get correct targets
for target in allTargets:
    name = target.Name()
    if name.find("Dispenser") != -1:
        correctCoverTargets.append(target)


window = tk.Tk()  # Sets the window from tk. In most tutorials this is called "root"

window.title("Gui")  # Sets the name of the window to "x"

window.update()

# Sets the dimentions of the window. In this case we structure it as a matrix.
window.rowconfigure([0, 1, 2], minsize=100, weight=1)
# Sets the dimentions of the window. In this case we structure it as a matrix.
window.columnconfigure([0], minsize=250, weight=1)


# Creates a function called donothing.
def donothing():
    YesButton.destroy()  # Destroys the buttons we create in the main.
    NoButton.destroy()
    welcometxt.destroy()

    # Set new dimentions of the window.
    window.rowconfigure([0, 1], minsize=100, weight=1)
    window.columnconfigure([0], minsize=250, weight=1)

    # Prints out some text on the window.
    label = tk.Label(text="Have a great day", bg='#58F')
    # Where to place the text in the created matrix.
    label.grid(row=1, column=0)

    # Magnus knows about this. Apparently you need to create updates for the window on the go.
    window.update()
    # time.sleep(3)  # Normal sleep function. 3 seconds.
    window.destroy()  # Destroys the entire window.


# Creates another function called placeorder.
def placeorder():

    YesButton.destroy()
    NoButton.destroy()
    welcometxt.destroy()

    window.rowconfigure([0, 1, 2, 3, 4, 5, 6, 7, 8], minsize=10, weight=1)
    window.columnconfigure([0], minsize=50, weight=1)
    window['background'] = '#58F'

    Colorconfig = tk.Label(text="Please select your desired smartphone configuration", font=(
        "times", 12, "bold"), bg='#58F')
    Colorconfig.grid(row=0, column=0)

    window.update()


##########################USER SELECTION#################################

# We define a function within a function. crazy. Its used to change the color of the dropdownmenu.

    def Color(selection):

        if selection == "Black":
            # , activebackground="black", activeforeground="white")
            popupmenu2.config(bg="black", fg="white")
        elif selection == "White":
            # , activebackground="white", activeforeground="black")
            popupmenu2.config(bg="white", fg="black")
        elif selection == "Blue":
            # , activebackground="blue", activeforeground="white")
            popupmenu2.config(bg="blue", fg="white")

    def CreateRoboDKProgram():
        # Colors in the RGBA type, where 0<=value<=1. Key/Value pairs in a dictionary.
        colors = {
            "Black": [0.2, 0.2, 0.2, 1],
            "Blue": [0, 0, 0.6, 1],
            "White": [0.6, 0.6, 0.6, 1]
        }

        coverSelectStatic = CoverSelect.get()
        ColorSelectStatic = ColorSelect.get()
        EngravingCheckStatic = EngravingCheck.get()
        numbOfPhonesStatic = numbOfPhones.get()

        def UpdateFrames():
            # If correcCoverFrames has contents, delete it.
            if len(correctCoverFrames) != 0:
                correctCoverFrames.clear()

            # Get the selected frame and append it into correctCoverFrames
            for frame in allFrames:
                name = frame.Name()
                if name.find(coverSelectStatic) != -1 and name.find(ColorSelectStatic) != -1:
                    correctCoverFrames.append(frame)

        # Get engraving programs
        engraveProgram = rdk.Item(
            "Engrave", itemtype=robolink.ITEM_TYPE_PROGRAM)
        shouldBeEngravedProgram = rdk.Item(
            "Should be engraved?", itemtype=robolink.ITEM_TYPE_PROGRAM)

        # Get objects
        curvedCover = rdk.Item(
            "Curved topcover assembly without bottom cover", itemtype=5)
        flatCover = rdk.Item("Flat Top Cover", itemtype=5)
        # Get conveyor robot.
        conveyor = rdk.Item("Conveyor")
        # Get station frame
        station = rdk.Item("Station", robolink.ITEM_TYPE_FRAME)

        # Modify the Zero Cover program in order to zero the correct cover.
        zeroProgram = rdk.Item(
            "Zero Cover", itemtype=robolink.ITEM_TYPE_PROGRAM)
        if zeroProgram.InstructionCount() != 0:
            zeroProgram.InstructionDelete(ins_id=0)
            zeroProgram.RunInstruction(
                "Zero " + coverSelectStatic + " Cover", run_type=robolink.INSTRUCTION_CALL_PROGRAM)

        # Delete current Pick Top Cover program if it already exist
        pickTopCoverProgram = rdk.Item(
            "Pick Top Cover", robolink.ITEM_TYPE_PROGRAM)
        if pickTopCoverProgram.Valid():
            rdk.Delete(pickTopCoverProgram)

        # Create new Pick top Cover Program
        moveDispenserProg = rdk.AddProgram("Pick Top Cover", robot)
        moveDispenserProg.setVisible(visible=False)
        moveDispenserProg.ShowInstructions(show=False)

        # Update the selected refernce frame.
        UpdateFrames()
        # Add instructions
        moveDispenserProg.setSpeed(speed_linear=100)
        # Specify the correct reference frame.
        moveDispenserProg.setPoseFrame(correctCoverFrames[0])
        # Move to, in and out of dispenser while grabbing the cover
        moveDispenserProg.RunInstruction("Open Gripper")
        moveDispenserProg.MoveJ(correctCoverTargets[0])
        moveDispenserProg.MoveL(correctCoverTargets[1])
        moveDispenserProg.RunInstruction("Close Gripper")
        moveDispenserProg.RunInstruction("Grab Cover")
        moveDispenserProg.MoveL(correctCoverTargets[0])

        def resetSimulation():
            # Update the dispenserframes, to get the selected reference frame every time
            UpdateFrames()
            # replace the "Set reference frame" instruction of the PickTopCoverProgram
            moveDispenserProg.InstructionDelete(ins_id=1)
            moveDispenserProg.InstructionSelect(ins_id=0)
            moveDispenserProg.setPoseFrame(correctCoverFrames[0])

            # If the engrave program already has an instruction, delete it.
            if engraveProgram.InstructionCount() != 0:
                engraveProgram.InstructionDelete(ins_id=0)
            # Add the new program call to the right engraving program (Curved or Flat), dependent on the selected type of cover
            engraveProgram.RunInstruction(
                coverSelectStatic, robolink.INSTRUCTION_CALL_PROGRAM)

            # decide if the engraving should be done (yes: calls everthing related to engraving)
            if int(EngravingCheckStatic):
                if shouldBeEngravedProgram.InstructionCount() == 0:
                    shouldBeEngravedProgram.RunInstruction(
                        "Everything Related To Engraving", robolink.INSTRUCTION_CALL_PROGRAM)

            # (no: remove the call to everything related to engraving)
            else:
                # Hide the laser.
                rdk.Item("Laser", itemtype=robolink.ITEM_TYPE_OBJECT).setVisible(
                    visible=False)
                if shouldBeEngravedProgram.InstructionCount() != 0:
                    shouldBeEngravedProgram.InstructionDelete(ins_id=0)

            # set specified color of the cover
            if coverSelectStatic == "Curved":
                # set the chosen color
                curvedCover.setColor(colors[ColorSelectStatic])
                # set the reference dispenser
                curvedCover.setParent(correctCoverFrames[0])
                # set the position relative to the parent.
                curvedCover.setPose(robodk.transl(
                    68, 58, 14) * robodk.rotx(90*pi/180))
                # remove the flat cover from working area
                flatCover.setParent(station)
                flatCover.setVisible(visible=False)

                # set the curved cover invisible
                curvedCover.setVisible(visible=True)
            else:
                # Set the flatcover to the specified color.
                flatCover.setColor(colors[ColorSelectStatic])
                # set the reference frame
                flatCover.setParent(correctCoverFrames[0])

                # Place the flat cover in the middle of the dispenser
                flatCover.setPose(robodk.transl(78.500, 82, 5)
                                  * robodk.rotz(-90*pi/180))

                # CurvedCover is made invisible and placed outside of the working area
                curvedCover.setVisible(visible=False)
                curvedCover.setParent(station)
                # Expose the flat cover
                flatCover.setVisible(visible=True)

            # Set the pallet to be at the beginning of the conveyor.
            conveyor.setPose(robodk.transl(-545.500,1042,874)*robodk.rotz(-90*pi/180))

        # Runs the main program N times

        def RunProgramNtimes():

            # Disable Place order button
            confirmOrder.configure(state=tk.DISABLED)
            # Set every program as invisible (no yellow path)
            allPrograms = rdk.ItemList(filter=robolink.ITEM_TYPE_PROGRAM)
            for prog in allPrograms:
                prog.setVisible(visible=False)

            # Repeat main program the specified number of times.
            for i in range(int(numbOfPhonesStatic)):
                resetSimulation()
                rdk.RunProgram("Main Prog", wait_for_finished=True)
                # Update progressbar depending on how many orders it has processed
                percentDone = (i+1) / int(numbOfPhonesStatic)*100
                progress.configure(value=percentDone)

            # Reenable the Place order button
            confirmOrder.configure(state=tk.NORMAL)
            # Set the progress to be zero again
            progress.configure(value=0)

        # Calling the RunProgramNtimes on a seperate thread. This allows the GUI to remain usable.
        threading.Thread(target=RunProgramNtimes).start()

    # Defines variable of type string. Used to keep track of the option.
    CoverSelect = tk.StringVar()
    # Defines variable of type string. Used to keep track of the option.
    ColorSelect = tk.StringVar()
    # Defines variable of type int. Used to keep track of the checkbox.
    EngravingCheck = tk.IntVar()
    # Defines variable of type int. Used to keep track of the number of orders.
    numbOfPhones = tk.IntVar()

    # Create a list of top cover variations
    TopCoverVariation = {'Flat', 'Curved'}
    CoverSelect.set('Flat')

    # Create a list of top cover colors
    TopCoverColor = {'Blue', 'White', 'Black'}
    ColorSelect.set('Black')  # Sets "black" as the default

    # Create a entry to give user possibility to add ordernumber.

    ChooseBottomLabel = tk.Label(
        text="Quantity", bg='#58F')
    ChooseBottomLabel.grid(row=2, column=0, padx=100, pady=0)

    numbOfPhones = tk.Entry()
    numbOfPhones.grid(row=3, column=0)

    # Create a dropdown menu with cover selection
    # The creation of the dropdown menu, using the "Optionmenu" widget from tk.
    popupmenu = tk.OptionMenu(window, CoverSelect, *TopCoverVariation)
    # padx and pady adds spacing (padding).
    popupmenu.grid(row=5, column=0, padx=100, pady=0)
    popupmenu.config(bg="lightgrey", fg="black")  # color of button.
    popupmenu["highlightthickness"] = 0  # Deletes border around button.

    ChooseBottomLabel = tk.Label(text="Cover type", bg='#58F')
    ChooseBottomLabel.grid(row=4, column=0, padx=100, pady=0)

    # Create a dropdown menu with color selection
    # The creation of the dropdown menu, using the "Optionmenu" widget from tk.
    popupmenu2 = tk.OptionMenu(
        window, ColorSelect, *TopCoverColor, command=Color)
    popupmenu2.grid(row=8, column=0, padx=100, pady=0)
    popupmenu2.config(bg="black", fg="white")  # color of button.
    # Deletes the border around the button.
    popupmenu2["highlightthickness"] = 0

    ChooseBottomLabel = tk.Label(
        text="Color", bg='#58F')
    ChooseBottomLabel.grid(row=7, column=0, padx=100, pady=0)

    # Create a checkbox
    CheckBox = tk.Checkbutton(
        window, text="Include engraving?", variable=EngravingCheck, bg='#58F')
    CheckBox.grid(row=9, column=0)

    # Create an orderbox
    confirmOrder = tk.Button(
        text="Place order", bg="lightgrey", state=NORMAL, command=CreateRoboDKProgram)
    confirmOrder.grid(row=10, column=1, sticky="nsew", padx=10, pady=10)

    # Create progress bar
    progress = ttk.Progressbar(
        window, orient=HORIZONTAL, length=100, mode='determinate', value=0)
    progress.grid(row=10, column=0, sticky="nsew", padx=10, pady=10)


# Main
welcometxt = tk.Label(text="Hello user, would you like to place an order?")
welcometxt.grid(row=0, column=0, sticky="nsew")

YesButton = tk.Button(text="Yes", width=25, height=0,
                      bg="green", command=placeorder)
YesButton.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

NoButton = tk.Button(text="No", width=25, height=0,
                     bg="red", command=donothing)
NoButton.grid(row=2, column=0, sticky="nsew", padx=10, pady=10)

window.update()


# Undersøg denne tk.menu


window.mainloop()


# ------------------------------------------------------------------------------------------------------------
# coverChoice = rdk.ItemUserPick("Selct top cover!",correctCoverFrames) #Already integrated but simple gui.

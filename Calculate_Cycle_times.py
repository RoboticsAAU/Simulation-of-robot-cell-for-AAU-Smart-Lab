from robolink import robolink
import json

rdk = robolink.Robolink()

program = rdk.Item("Main Prog", robolink.ITEM_TYPE_PROGRAM)

robot = program.getLink(robolink.ITEM_TYPE_ROBOT)

writeline = "Linear speed (mm/s)\tJoint Speed (deg/s)\tCycle Time(s)"
print(writeline)

msg_html = "<table border=1><tr><td>" + \
    writeline.replace('\t', '</td><td>')+"</td></tr>"


def AnalyzeProgram(tempProgram):
    # progTime = 0
    result = tempProgram.Update()
    instructions, time, travel, ok, error = result
    # progTime += time

    for insId in range(tempProgram.InstructionCount()):
        # print(tempProgram.Name())
        instruction_dict = tempProgram.setParam(insId)

        # print(instruction_dict)

        if instruction_dict['Type'] == 8:
            # print("Time: " + str(time) + " ---- of: " +
            #   tempProgram.Name() + "\n Total time: " + str(progTime))
            # print("Call recursive: " +
            #   instruction_dict['Code'] + ", Instruction: %.1f " % insId)
            time += AnalyzeProgram(
                rdk.Item(instruction_dict['Code'], robolink.ITEM_TYPE_PROGRAM))
            # print("Program time: " + str(progTime))
    return time


# Starting speeds
linearSpeed = 250  # mm/s
jointSpeed = 380  # deg/s


# Stepsize
stepsize = 1

# Desired time to reach
desiredTime = 27


robot.setSpeed(linearSpeed, jointSpeed)
totalTime = AnalyzeProgram(program)
print(totalTime)
while totalTime > desiredTime:
    linearSpeed += stepsize
    jointSpeed += stepsize
    robot.setSpeed(linearSpeed, jointSpeed)
    totalTime = AnalyzeProgram(program)
    # print(totalTime)
    # print("Itterative time: " + str(totalTime))

    result = program.Update()

    instructions, time, travel, ok, error = result

    # insId = 0
    # while insId < instructions:
    #     instruction_dict = program.setParam(insId)
    #     print("\nInstruction: " + str(insId))
    #     print(instruction_dict)
    #     insId += 1
    # print("Total time: " + str(AnalyzeProgram(program)))

    newline = "%.1f\t%.1f\t%.1f" % (
        linearSpeed, jointSpeed, totalTime)
    # print(newline)

    msg_html = msg_html + '<tr><td>' + \
        newline.replace('\t', "</td><td>") + '</td></tr>'

msg_html = msg_html + '</table>'

rdk.ShowMessage(msg_html)

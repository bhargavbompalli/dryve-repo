import time

import dryveCodeFIXED
import createdryverail

def simple_demo_move():
    dryveCodeFIXED.targetPosition(2500)
    #time.sleep(2)
    #dryveCodeFIXED.targetPosition(90)
    #time.sleep(2)
    #dryveCodeFIXED.targetPosition(1900)
    #time.sleep(2)
    #dryveCodeFIXED.targetPosition(600)

def main():
    #dryveCodeFIXED.establishConnection()
    #dryveCode.startProcedure()
    dryveCodeFIXED.dryveInit()
    #dryveCodeFIXED.homing()
    #print("Initialization started...")
    dryveCodeFIXED.profileVelocity(800)
    position1 = dryveCodeFIXED.getPosition()
    print(position1)
    print("Moving to position")
    #dryveCodeFIXED.setUnitPosition(0x01, 0xfc)
    #dryveCodeFIXED.targetPosition(10)
    simple_demo_move()
    print("Reached position 1")
    position2 = dryveCodeFIXED.getPosition()
    print(position2)
    #"Moving to target position..."

if __name__ == '__main__':
    main()
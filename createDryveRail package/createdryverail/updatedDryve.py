import socket
import time

def get_socket(hostname, port):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except socket.error:
        print("failed to create sockt")

    s.connect((hostname, port))
    print("Socket created")
    return s


# Statusword 6041h
# Status request
status = [0, 0, 0, 0, 0, 13, 0, 43, 13, 0, 0, 0, 96, 65, 0, 0, 0, 0, 2]
status_bytes = bytearray(status)
print("status bytes", status_bytes)

# Controlword 6040h
# Command: Shutdown
shutdown = [0, 0, 0, 0, 0, 15, 0, 43, 13, 1, 0, 0, 96, 64, 0, 0, 0, 0, 2, 6, 0]
shutdown_bytes = bytearray(shutdown)
print("shutdown bytes", shutdown_bytes)

# Controlword 6040h
# Command: Switch on
switchOn = [0, 0, 0, 0, 0, 15, 0, 43, 13, 1, 0, 0, 96, 64, 0, 0, 0, 0, 2, 7, 0]
switchOn_bytes = bytearray(switchOn)
print("switchon bytes", switchOn_bytes)

# Controlword 6040h
# Command: enable Operation
enableOperation = [0, 0, 0, 0, 0, 15, 0, 43, 13, 1, 0, 0, 96, 64, 0, 0, 0, 0, 2, 15, 0]
enableOperation_bytes = bytearray(enableOperation)
print("enable ops bytes", enableOperation_bytes)

# Controlword 6040h
# Command: reset dryve
reset = [0, 0, 0, 0, 0, 15, 0, 43, 13, 1, 0, 0, 96, 64, 0, 0, 0, 0, 2, 0, 1]
reset_bytes = bytearray(reset)
print("reset array", reset_bytes)


def sendCommand(s, data):
    s.send(data)
    res = list(s.recv(24))
    print("received resp:", res)
    return res


def set_shutdown(s):
    """Send the shutdown controlword and retry until system state is OK."""
    system_ok_1 = [0, 0, 0, 0, 0, 15, 0, 43, 13, 0, 0, 0, 96, 65, 0, 0, 0, 0, 2, 33, 6]
    system_ok_2 = [0, 0, 0, 0, 0, 15, 0, 43, 13, 0, 0, 0, 96, 65, 0, 0, 0, 0, 2, 33, 22]
    system_ok_3 = [0, 0, 0, 0, 0, 15, 0, 43, 13, 0, 0, 0, 96, 65, 0, 0, 0, 0, 2, 33, 2]

    res = sendCommand(s, shutdown_bytes)
    while (res := sendCommand(s, status_bytes)) not in [system_ok_1, system_ok_2, system_ok_3]:
        print("wait for shdn")
        time.sleep(1)


def set_switch_on(s):
    """Send the switch on control word and wait for OK status"""
    # Look at Bit assignment Statusword, data package in user manual
    swon_ok_1 = [0, 0, 0, 0, 0, 15, 0, 43, 13, 0, 0, 0, 96, 65, 0, 0, 0, 0, 2, 35, 6]
    swon_ok_2 = [0, 0, 0, 0, 0, 15, 0, 43, 13, 0, 0, 0, 96, 65, 0, 0, 0, 0, 2, 35, 22]
    swon_ok_3 = [0, 0, 0, 0, 0, 15, 0, 43, 13, 0, 0, 0, 96, 65, 0, 0, 0, 0, 2, 35, 2]

    res = sendCommand(s, switchOn_bytes)
    while (res := sendCommand(s, status_bytes)) not in [swon_ok_1, swon_ok_2, swon_ok_3]:
        print("wait for sw on")
        time.sleep(1)


def set_operation_enabled(s):
    """Send the operation enable controlword."""
    known_open_1 = [0, 0, 0, 0, 0, 15, 0, 43, 13, 0, 0, 0, 96, 65, 0, 0, 0, 0, 2, 39, 6]
    known_open_2 = [0, 0, 0, 0, 0, 15, 0, 43, 13, 0, 0, 0, 96, 65, 0, 0, 0, 0, 2, 39, 22]
    known_open_3 = [0, 0, 0, 0, 0, 15, 0, 43, 13, 0, 0, 0, 96, 65, 0, 0, 0, 0, 2, 39, 2]

    res = sendCommand(s, enableOperation_bytes)
    while (res := sendCommand(s, status_bytes)) not in [known_open_1, known_open_2, known_open_3]:
        print("wait for op en")
        time.sleep(1)


def set_mode(s, mode):

    # Setzen der Operationsmodi im Objekt 6060h Modes of Operation
    # Set operation modes in object 6060h Modes of Operation
    sendCommand(s, bytearray([0, 0, 0, 0, 0, 14, 0, 43, 13, 1, 0, 0, 96, 96, 0, 0, 0, 0, 1, mode]))
    expected_result = [
        0,
        0,
        0,
        0,
        0,
        14,
        0,
        43,
        13,
        0,
        0,
        0,
        96,
        97,
        0,
        0,
        0,
        0,
        1,
        mode,
    ]

    while sendCommand(s, bytearray([0, 0, 0, 0, 0, 13, 0, 43, 13, 0, 0, 0, 96, 97, 0, 0, 0, 0, 1])) != expected_result:
        print("wait for mode")
        time.sleep(1)


def home(s):

    # Parametrierung der Objekte gemäß Handbuch
    # Parameterization of the objects according to the manual

    # 6060h Modes of Operation
    # Set Homing mode (see "def set_mode(mode):"; Byte 19 = 6)
    set_mode(s, 6)

    # 6092h_01h Feed constant Subindex 1 (Feed)
    # Set feed constant to 6000; refer to manual (Byte 19 = 112; Byte 20= 23)
    sendCommand(s, bytearray([0, 0, 0, 0, 0, 15, 0, 43, 13, 1, 0, 0, 96, 146, 1, 0, 0, 0, 2, 112, 23]))

    # 6092h_02h Feed constant Subindex 2 (Shaft revolutions)
    # Set shaft revolutions to 1; refer to manual (Byte 19 = 1)
    sendCommand(s, bytearray([0, 0, 0, 0, 0, 14, 0, 43, 13, 1, 0, 0, 96, 146, 2, 0, 0, 0, 1, 1]))

    # 6099h_01h Homing speeds Switch
    # Speed during search for switch is set to 60 rpm (Byte 19 = 112; Byte 20 = 23))
    sendCommand(s, bytearray([0, 0, 0, 0, 0, 15, 0, 43, 13, 1, 0, 0, 96, 153, 1, 0, 0, 0, 2, 112, 23]))

    # 6099h_02h Homing speeds Zero
    # Set speed during Search for zero to 60 rpm (Byte 19 = 112; Byte 20 = 23))
    sendCommand(s, bytearray([0, 0, 0, 0, 0, 15, 0, 43, 13, 1, 0, 0, 96, 153, 2, 0, 0, 0, 2, 112, 23]))

    # 609Ah Homing acceleration
    # Set Homing acceleration to 500 rpm/min² (Byte 19 = 80; Byte 20 = 195)
    sendCommand(s, bytearray([0, 0, 0, 0, 0, 15, 0, 43, 13, 1, 0, 0, 96, 154, 0, 0, 0, 0, 2, 80, 195]))

    # 6040h Controlword
    # Start Homing
    sendCommand(s, bytearray([0, 0, 0, 0, 0, 15, 0, 43, 13, 1, 0, 0, 96, 64, 0, 0, 0, 0, 2, 31, 0]))

    # Check Statusword nach Referenziert Signal
    # Check Statusword for signal referenced
    while sendCommand(s, status_bytes) != [0, 0, 0, 0, 0, 15, 0, 43, 13, 0, 0, 0, 96, 65, 0, 0, 0, 0, 2, 39, 22]:

        print("wait for Homing to end")

        # 1 Sekunde Verzoegerung
        # 1 second delay
        time.sleep(1)


def int_to_le_bin(x):
    """Returns the 4 bytes representing the given int"""
    raw_bin_str = bin(x)[2:]

    bytes_to_ret = []
    prev_val = None
    for i in range(1, 5):
        start_val = -8 * i
        str_bits = raw_bin_str[start_val:prev_val]
        int_bits = int(str_bits or "0", 2)
        bytes_to_ret.append(int_bits)
        prev_val = start_val

    return bytes_to_ret


def demo_motor(s, velocity: int, acceleration: int, revs: int):
    sendCommand(s, enableOperation_bytes)

    # 6060h Modes of Operation
    # Set Profile Position Mode (see "def set_mode(mode):"; Byte 19 = 1)
    set_mode(s, 1)

    # 6081h Profile Velocity
    # Set velocity to 60 rpm == 6000 (Byte 19 = 112; Byte 20 = 23)
    rpm_bytes = int_to_le_bin(velocity * 100)
    sendCommand(s, bytearray([0, 0, 0, 0, 0, 15, 0, 43, 13, 1, 0, 0, 96, 129, 0, 0, 0, 0, 2] + rpm_bytes[:2]))

    # 6083h Profile Acceleration
    # Set acceleration to 500 rpm/min² == 50000 (Byte 19 = 80; Byte 20 = 195)
    acceleration_bytes = int_to_le_bin(acceleration * 100)
    sendCommand(s, bytearray([0, 0, 0, 0, 0, 15, 0, 43, 13, 1, 0, 0, 96, 131, 0, 0, 0, 0, 2] + acceleration_bytes[:2]))

    # Set start position
    setPosition0 = 0
    setPosition1 = 0
    setPosition2 = 0
    setPosition3 = 0

    # Clockwise/counter-clockwise motor movement Loop
    while True:

        # Reset target position after each loop; the variables setPositionX are rewritten with the default value after each loop
        # Send position to SDO 607Ah
        # 607Ah == int('607A', 16)
        # or int('60', 16) and int('7A', 16)
        # See page 157
        sendCommand(
            s,
            bytearray(
                [
                    0,
                    0,
                    0,
                    0,
                    0,
                    17,
                    0,
                    43,
                    13,
                    1,
                    0,
                    0,
                    96,  # SDO Object 1
                    122,  # SDO Object 2
                    0,
                    0,
                    0,
                    0,
                    4,
                    setPosition0,
                    setPosition1,
                    setPosition2,
                    setPosition3,
                ]
            ),
        )

        print("go")

        # Set Bit 4 true to excecute the movoment of the motor
        sendCommand(s, bytearray([0, 0, 0, 0, 0, 15, 0, 43, 13, 1, 0, 0, 96, 64, 0, 0, 0, 0, 2, 31, 0]))

        # delay
        time.sleep(velocity / 60 * revs)

        # Check Statusword for target reached
        while sendCommand(s, status_bytes) != [0, 0, 0, 0, 0, 15, 0, 43, 13, 0, 0, 0, 96, 65, 0, 0, 0, 0, 2, 39, 22]:

            print("wait for next command")
            time.sleep(1)

        sendCommand(s, enableOperation_bytes)

        if setPosition0:
            setPosition0, setPosition1, setPosition2, setPosition3 = [0, 0, 0, 0]
        else:
            # Half a turn
            # setPosition0, setPosition1, setPosition2, setPosition3 = int_to_le_bin(int(velocity / 2 * 100))
            # FUll turn
            setPosition0, setPosition1, setPosition2, setPosition3 = int_to_le_bin(velocity * revs * 100)


def init(s):
    sendCommand(s, reset_bytes)
    set_shutdown(s)
    set_switch_on(s)
    set_operation_enabled(s)


def main():
    """Run the demo program"""
    s = get_socket("2.tcp.ngrok.io", 19928)
    init(s)
    home(s)

    RPM = 120
    ACCEL = 500
    # TODO: Revs wanted isn't working correct. Something about the math of how the RPMs work
    REVOLUTIONS_WANTED = 1

    demo_motor(s, RPM, ACCEL, REVOLUTIONS_WANTED)


if __name__ == "__main__":
    main()
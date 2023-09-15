#
# ┌─────────────┐         ┌─────────────┐
# │ Transmit Tx ├────────►│ Rx Receive  │
# │             │         │             │
# │             │         │             │
# │ Receive  Rx │◄────────┤ Tx Transmit │
# │             │         │             │
# │             │         │             │
# │ doorBell Bo ├────────►│ Bi doorBell │
# │   Out       │         │      In     │
# │             │         │             │
# │ doorBell Bi │◄────────┤ Bo doorBell │
# │   In        │         │      Out    │
# └─────────────┘         └─────────────┘

if argv[1] == "-master":                  # Run this instance as master
    bRx = True                              # Master is signified by bRx = TRUE
else:
    bRx = False
if arv[2] == "-wStop":                    # Enable TxStop protocol enhancement
    benStop = True
else:
    benStop = False
if arv[3] == "-wSack":                    # Enable RxStopACK protocol enhancement
    benSack = True
else:
    bSack = False

rx = tx = bo = bi = 0                     # Initialize all 4 databits low
bTxStop = bRxStop = bSwap = False         # Use to swap Master / Slave and control stop

def Init():                               # Initialize all GPIOs low
    initp(TX, OUT, LOW)
    initp(RX, IN, PLOW)
    initp(BO, OUT, LOW)
    initp(BI, IN, PLOW)

def RxWait():                             # RxWait routine, run by master
    while True:                           # Until break
        if bi != getp(BI):                # Wait for Incomming doorBell signaling data on RX
            bi = inv(bi)                    # Save doorBell state
            rx = getp(RX)                 # Pull data off RX since we got heard the doorBell
            process(rx)                   # Do whatever process with the recieved data
            if bSwap == True:             # Set by process routine to signal a desire to Tx instead of Rx
                break                       # Break back to main for it to trigger swap
            bHalfStop = False             # Reset stop detection since we heard the doorBell
            bo = inv(bo)                  # Done with data, request another bit
            setp(BO, bo)
        elif benStop and rx != getp(RX):  # TxStop protocol will pulse our RX without pulsing our BI
            rx = inv(rx)                  # Save RX so we can see if it flipps again withotu BI
            if bHalfStop:                 # If this is the second state change, we've recieved a TxStop command
                bRxStop = True              # note that we've recived it and perform RxStopACK if enabled
                break
            else:                         # Otherwise we are only half way through a stop operation
                bHalfStop = True

def TxWait():                             # TxWait routine, run by slave
    while True:                           # Until break
        if bi != getp(BI):                # Wait for Incomming doorBell signalling ready to recieve
            bi = inv(bi)                    # Save doorBell state
            tx = generate()               # Get the next bit of data to send
            if bTxStop:
                break
            setp(TX, tx)                    # Send data
            bo = inv(bo)
            setp(BO, bo)                    # Alert that data is waiting
        elif 0 != getp(RX):               # If we our (slave) RX goes high, a swap is requested
            bSwap = True                    # Signal swap and fall back to main
            break

def Swap():                               # Swap routine master / slave roles, called externally (see bSwap / process())
    bSwap = False                           # Now that we are processing, turn off indicator
    if(bRx):                              # Will swap from master (Rx) to slave (Tx)
        bRx = False                         # Set boolean that we are slave
        tx = 1                              # (Former) master starts swap by clocking out TX without BO
        setp(TX,tx)                         # Clock out TX without BO to start swap
    else:                                 # Will swap from slave (Tx) to master (Rx)
        bRx = True                          # Set boolean that we are master
        tx = 0                              # As master TX is reserved for swap commands
        setp(TX,tx)                         # Set TX to default low
        ob = inv(ob)                        # As master we start the message pump by ringing the bell
        setp(OB,op)                         # Ring the bell

def TxStop():                             # Handle TxStop protocol, called externally (see bTxStop / generate())
    # assert benStop==True
    # assert bRx==False
    for i in range (0, 1000):             # We (slave) will toggle TX without BO
        tx = inv(tx)                        # Toggle TX without BO
        setp(TX,tx)
        if benSack and rx != getp(RX):    # If RxStopACK is enabled, see if they (master) toggle our RX in reply
            rx = inv(rx)
            if bHalfSack:                 # If this is the second toggle
                bSack = True                # record that RxStopACK recieved and release to main
                break
            else:                         # If this is the first toggle, wait for second
                bHalfSack = True
        delay(1)                          # sleep one MS

def main():                               # Main program where all the goodness happens
    Init()                                # Run init to turn everything low
    while True:                           # Run for ever
        if bRx:                             # Master receives
            RxWait()
        else:                               # Slave transmits
            TxWait()
        if bSwap:                         # Did we recieve a swap command?
            Swap()                          # Do swap
        if benStop and bTxStop and not bRx: # Do we (slave) need to signal a TxStop?
            TxStop()                        # Do TxStop
            if bSack:                       # If we (slave) received a RxStopACK
                exit(0)                       # Exit happy happy
            else:                           # If we didn't recieve RxStopACK
                exit(1)                       # Exit sad sad
        if benStop and bRxStop and bRx:     # We (master) sensed a TxStop on the protocol
            if benSack:                       # If RxStopACK is enabled, do a RxStopACK
                for i in range (0, 300):      # They (slave) will drop as soon as they see two, so we don't need many
                    tx = inv(tx)
                    setp(TX,tx)
                    delay(1)                  # delay one ms
            exit()                            # Wether RxStopACK is enabled or not, we're gone

                                          # THAT'S ALL FOLKS!
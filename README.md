# 4-IN 16-OUT Multiplexor

This repo contains datasheets, E-CAD and and the Controlling software of the Multiplexor device

The need:

In order for a devices to be tested against multiple use case devices and or lab instruments with out intervention in a single test setup, it is nessisary to have a way to replace the manual process of making the physical connections between the devices. By removing this step, much larger test sequences can be made by chaining together smaller sequences that would otherwise be seperated by manual connection changes. This devices serves to remove or greatly reduce the necessity of reconfiguration. This device is designed to be modular and be used in conjuction with other devices being developed. 

ex: Imagine 16 DC use case devices, connected to 4 yetis simultaneously which are toggled X number of times. Total connections = (#of yetis) X (# of devices) X (# of repeats). If X were 30 for statistical signifigance - that would be 1920 connections a technicial would have to make for just those 16 use cases devices. We currently have over 100 use case devices that are tested each regression. 

Description: 

This device is created such that 8 inputs can be directed to any of the 32 output lines and for the most part run simultaniously with some exceptions. Sets of DPDT relays make the connections and move the paths in pairs(either + - or Hot Neutral) effectively making the device 4 input pairs to any 16 output pairs. It is also worth noting that the terms input and output are loosly defined here and there is no reason one could not use the 16 outputs as inputs and vice versa. The device is rated up to 400V before its creepage requirments are invalidated(AC or DC)and up to 30A of Current. The necissary condition to ensure that the 4 inputs can be connected to the 16 outputs simultaniously is that the electrical paths for each input, output pair must not share a common bus at any point or in other words "cross". To see if paths "cross" refer to the control diagram in firware which shows how the relays create the paths. Typically it is possible for all inputs to be connected to the desired outputs at once. 

An I2C bus connects to 4 slave devices which each have gpio pins. These pins are used to control the state of each relay. The identifier of the relay on the board and the path diagram is labeled as follows(controlling slave #, bit position of gpio register that controls it). The i2c address is adjustable via address select resistors with up to 8 unique  on each bus. The control software is in python and has preconfigured functions which simply allow the user to state which input --> output connects should be made as well as the duration the connection should last. The nessisary steps to disconnect the live signals, make the path changes, check for short circuits, and over all ensure the isolated pathways are delt with correctly is all handled automatically. 


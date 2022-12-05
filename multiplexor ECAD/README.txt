12/01/2022 -- A EMI issue was found where ESD on a nearby conductor could produce an EMI wave that would pull the reset pin on each i2c to GPIO low enough to
trigger Reset. To combate this a .1uf cap was added to each each reset pin to short high frequency signals(200khz was the emi packet)to ground.
A simple 1k resistor was also added between reset and the pi's ground to then bleed off those caps when no power is connected. Additionally the
the supply voltage has been bumped up to 5V from 3.3V. This appears to have fixed the issue. 
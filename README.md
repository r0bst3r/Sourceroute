# Sourceroute
Do you have multiple nics in linux?  Ever done a ip route show and realized that linux is only using one of the nics for
outbound traffic?  This issue explained in greater detail at 
https://kindlund.wordpress.com/2007/11/19/configuring-multiple-default-routes-in-linux/.  

This python script automates the manual procedure listed on that webpage, by determining the ip information needed and
 running the iproute2 utilities to install those ip rules.
 
Installation:
- Requires Python 3.
- Install required libraries by doing a: pip install -r requirements.txt

Usage:
Add rules for an interface by doing python3 Sourceroute.py --up InterfaceName
Delete rules for an interface by doing python3 Sourceroute.py --down InterfaceName

This may be able to be automated in linux by using the if-up.local script.

If you have any suggestions feel free to contact me.
 
 Robbie Wilson
 robbie@robbiewilson.com

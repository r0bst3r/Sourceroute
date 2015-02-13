class Sourceroute():

    def find_gateway(action, iface):
        import netaddr
        import netifaces as ni
        import sys

        ifaceaddr = None
        netmask = None

        # Pull ip address for current interface, and handle errors if they exist
        try:
            ifaceaddr = ni.ifaddresses(iface)[2][0]['addr']
            netmask = ni.ifaddresses(iface)[2][0]['netmask']
            #print('SOURCEROUTE:', iface, ifaceaddr, netmask)
        except ValueError:
            print("You must specify a valid interface name")
            sys.exit(1)
        except KeyError:
            print("ERROR: There is no ip address configured on: " + iface)
            print("Testing will be skipped on this inteface. Please verify ip's on all active interfaces and try again.")
            print("")

        # Create variable with address in CIDR notation
        ip = netaddr.IPNetwork(ifaceaddr + '/' + netmask)
        cidraddr = ip

        # Create network address for subnet
        networkaddr = str(ip.network) + '/' + str(ip.prefixlen)

        # Create gateway address variable
        gateway = ip.network + 1

        # Create interface host address
        hostaddr = str(ifaceaddr + '/32')

        if action == 'cidr':
            return cidraddr

        if action == 'networkaddr':
            return networkaddr

        if action == 'ifaceaddr':
            return ifaceaddr

        if action == 'gateway':
            return gateway
        if action == 'hostaddr':
            return hostaddr
        else:
            return

    def rt_table(action, iface):
        # From http://www.snip2code.com/Snippet/136347/Simple-rt_tables-parser
        rt_tables = '/etc/iproute2/rt_tables'
        res = {}

        def rttableparser(action=None):
            import re


            def get_tables():
                state = {}

                def line_filter(s):
                    if len(s) == 0 or state['discard']:
                        return False
                    if s.find('#') >= 0:
                        state['discard'] = True
                        return False
                    return True

                with open(rt_tables, 'r') as f:
                    for line in f:
                        state['discard'] = False
                        l = list(
                            filter(
                                line_filter,
                                re.split(
                                    '[\s\t]+',
                                    line.strip()
                                )
                            )
                        )

                        if len(l) < 2:
                            continue

                        number, label = l

                        # Robbie Added - Make numbers ints for Min function
                        intnum = int(l[0])
                        l[0] = intnum

                        res[intnum] = label

                return res

            def low():
                return(min(get_tables()))

            def findfreetablenum():
                starttablenum = low()+1

                loop = True
                while loop is True:

                    x = {}
                    x = get_tables()

                    try:
                        value = x[starttablenum]
                    except KeyError:
                        # Key is not present, so we can use it!
                        loop = False
                        return starttablenum

                    starttablenum += 1

            if action == 'low':
                return int(low())
            if action == 'freenum':
                return findfreetablenum()
            else:
                return get_tables()



        def add_table(iface):

            freenum = rttableparser('freenum')

            def write_table():
                """We need to add a routing table with the first free number, and using the interface name
                from article echo "1 admin" >> /etc/iproute2/rt_tables
                return
                """
                f = open(rt_tables, 'w')
                f.write('#' + '\n')

                for key, value in res.items():
                    f.write(str(key) + '\t' + value + '\n')

                f.write('#')
                f.close()

            print('SOURCEROUTE - Adding routing table:', freenum, iface)

            res[freenum] = iface

            write_table()

        def match(iface):
            rttableparser()
            if iface in res.values():
                print("SOURCEROUTE - This table already exists", iface)
                return True
            else:
                print("SOURCEROUTE - This table doesn't exist, we need to make one!!")
                add_table(iface)

        # Function Actions
        if action == 'read':
            print(rttableparser())
        if action == 'low':
            print(rttableparser('low'))
        if action == 'freenum':
            print(rttableparser('freenum'))
        if action == 'addtable':
            add_table(iface)
        if action == 'match':
            match(iface)
        else:
            match(iface)
        # /Function Actions

    def add_routes(iface):
        import subprocess

        # Make sure rt_table exists, and if not make it
        Sourceroute.rt_table('match', iface)

        """
        Make Routes like following:
        ip route add 10.10.70.0/24 dev eth0 src 10.10.70.38 table admin
        ip route add default via 10.10.70.254 dev eth0 table admin
        """
        cmd1 = str('ip route add ' + str(Sourceroute.find_gateway(iface)) + ' dev ' + iface + ' src ' + str(Sourceroute.find_gateway(
            iface)) + ' table ' + iface)
        print('Command 1: ', cmd1)
        a = subprocess.check_output(cmd1, shell=True, stderr=subprocess.STDOUT)
        print(a)


        cmd2 = str('ip route add default via ' + str(Sourceroute.find_gateway(iface)) + ' dev ' + iface + ' table ' + iface)
        print('Command 2: ', cmd2)
        b = subprocess.check_output(cmd2, shell=True, stderr=subprocess.STDOUT)
        print(b)

        """
        ip rule add from 10.10.70.38/32 table admin
        ip rule add to 10.10.70.38/32 table admin
        """
        cmd3 = str('ip rule add from ' + str(Sourceroute.find_gateway(iface)) + ' table ' + iface)
        print('Command 3: ', cmd3)
        c = subprocess.check_output(cmd3, shell=True, stderr=subprocess.STDOUT)
        print(c)

        cmd4 = str('ip rule add to ' + str(Sourceroute.find_gateway(iface)) + ' table ' + iface)
        print('Command 4: ', cmd4)
        d = subprocess.check_output(cmd4, shell=True, stderr=subprocess.STDOUT)
        print(d)

    def del_routes(iface):
        import subprocess
        """
        ip route del 10.10.70.0/24 dev eth0 src 10.10.70.38 table admin
        ip route del default via 10.10.70.254 dev eth0 table admin
        """
        cmd1 = str('ip route del ' + str(Sourceroute.find_gateway(iface)) + ' dev ' + iface + ' src ' + str(Sourceroute.find_gateway(
            iface)) + ' table ' + iface)
        print('Command 1: ', cmd1)
        a = subprocess.check_output(cmd1, shell=True, stderr=subprocess.STDOUT)
        print(a)


        cmd2 = str('ip route del default via ' + str(Sourceroute.find_gateway(iface)) + ' dev ' + iface + ' table ' + iface)
        print('Command 2: ', cmd2)
        b = subprocess.check_output(cmd2, shell=True, stderr=subprocess.STDOUT)
        print(b)

        """
        ip rule del from 10.10.70.38/32 table admin
        ip rule del to 10.10.70.38/32 table admin
        """
        cmd3 = str('ip rule del from ' + str(Sourceroute.find_gateway(iface)) + ' table ' + iface)
        print('Command 3: ', cmd3)
        c = subprocess.check_output(cmd3, shell=True, stderr=subprocess.STDOUT)
        print(c)

        cmd4 = str('ip rule del to ' + str(Sourceroute.find_gateway(iface)) + ' table ' + iface)
        print('Command 4: ', cmd4)
        d = subprocess.check_output(cmd4, shell=True, stderr=subprocess.STDOUT)
        print(d)

def startup():
    import argparse
    import os
    import sys

    parser = argparse.ArgumentParser(description='Configures sourced based routing on specified interface')
    parser.add_argument(help='Interface Name', action='store', dest='iface')
    parser.add_argument('-Up', '--up', action='store_true', help="Up interface Routine, find gateway, add rt_table, add routes and rules")
    parser.add_argument('-Down', '--down', action='store_true', help="Down interface Routine, Delete routes and rules")
    parser.add_argument('-Gateway', '--gateway', action='store_true', help="Find Gateway for Interface")
    parser.add_argument('-Cidr', '--cidr', action='store_true', help="Cidr Address for Interface")
    parser.add_argument('-reparse', '--reparse', action='store_true', help="reparse - Debug")
    parser.add_argument('-low', '--low', action='store_true', help="Lowest Key - Debug")
    parser.add_argument('-freenum', '--freenum', action='store_true', help="freenum - Debug")
    parser.add_argument('-match', '--match', action='store_true', help="See if table exists, and then add it - Debug")
    parser.add_argument('-addtable', '--addtable', action='store_true', help="Add rt_table - Debug")


    args = parser.parse_args()

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)
    if args.gateway:
        print(Sourceroute.find_gateway(args.iface))
    if args.cidr:
        print(Sourceroute.find_gateway(args.iface))
    if args.reparse:
        Sourceroute.rt_table('read', args.iface)
    if args.low:
        Sourceroute.rt_table('low', args.iface)
    if args.freenum:
        Sourceroute.rt_table('freenum', args.iface)
    if args.addtable:
        Sourceroute.rt_table('addtable', args.iface)
    if args.match:
        Sourceroute.rt_table('match', str(args.iface))
    if args.up:
        Sourceroute.add_routes(args.iface)
    if args.down:
        Sourceroute.del_routes(args.iface)

startup()
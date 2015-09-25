#coding=utf-8
import os
import re
import time
import threading
import subprocess
from optparse import OptionParser
import ucore


def main():
    parse = OptionParser()
    parse.add_option('-f', '--file', dest='listfile', help='case or list to run', action='store')
    parse.add_option('-s', '--serial', dest='serialno', help='which device to run', action='store')
    parse.add_option('-c', '--count', dest='count', help='how many times to run', action='store', default='1')
    parse.add_option('-r', '--reportdir', dest='reportdir', help='where to capture report', action='store', default=".")
    parse.add_option('-j', '--jar', dest='jarpath', help='which jar to run', action='store')
    parse.add_option('-k', '--apk', dest='apkpath', help='if apk should install', action='store')
    (option, args) = parse.parse_args()

    a = ucore.ADB(option.serialno)
    product = a.adbshell('getprop ro.product.name')
    version = a.adbshell('getprop ro.build.description')
    if option.jarpath != None:
        a.push(option.jarpath)
    else:
        ucore.log.debug('no uiautomator package found!')
    if option.apkpath != None:
        a.install(option.apkpath)
    else:
        ucore.log.debug('no apk to install!')
    if option.serialno == None:
        raise ucore.AdbException('Error: MUST specify a serial number!')
    count = int(option.count)
    suite = ucore.TestSuite()
    for i in range(count):
        suite.addTestCase(option.listfile)

    runner = ucore.TextRunner(a, option)

    runner.startSuite(suite)
    ucore.HtmlReport(suite.tests, locals())


    """
    try:
        runner.startSuite(suite)
    except:
        #generate html report here
        print 'runner Exception'
        import html
        html.HtmlReport(suite.tests, runner.report_dir)

    """

    print '\nLog Directory: %s \n' %runner.report_dir

if __name__ == '__main__':
    main()

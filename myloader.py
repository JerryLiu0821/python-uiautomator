#coding=utf-8
import os, time, re
import subprocess
import logging
import threading
from optparse import OptionParser

#logging.basicConfig(level=logging.DEBUG)

class AdbException(Exception):
    def __init__(self,message):
        Exception.__init__(self,message)


class TestCase():
    def __init__(self, jar, caselist):
        self.jar = jar+".jar"
        self.names = []
        if isinstance(caselist, list):
            for line in caselist:
                self.names.append(line.strip())
        else:
            self.names.append(castlist.strip())
        self.result = None
        self.output = ""
        self.errorinfo = ""
        self.runtime = ""
        self.descriptive = ""
        self.logDirectory = None
        self.resultDirectory = None

    def uicommand(self):
        """return a uiautomator string command """
        uicmd = self.jar
        for line in self.names:
            uicmd = uicmd + " " + "-c " + line

        return uicmd

class TestSuite():
    def __init__(self):
        self.test = []

    def loadTestFromName(self, name):
        """return single TestCase instance """
        case = self._convertCastList(name)
        test = TestCase(case[0], case[1])
        self.test.append(test)
        return test

    def loadTestFromFile(self, filename):
        """ return TestCase list for all case in given file """
        test = []
        with open(filename, "r+") as fp:
            for line in fp:
                if line != "" and not line.startswith("#"):
                    test.append(self.loadTestFromName(line))
        return test

    def _convertCastList(self, casestr):
        """return a tuple contain jar, and castlist"""
        castlist = []
        names = casestr.split(",")
        for name in names:
            castlist.append(name.split(".", 1)[1])
        return names[0].split(".", 1)[0], castlist

    def runTest(self, test):
        pass


    def runSuite(self):
        """run this test suite as a case"""
        pass


def adbhook(f):
    def dec():
        adb = run_sh_command('adb devices')
        adb = adb.split(os.linesep)
        if 'not found' in adb[0]:
            raise AdbException("adb command not found")
        return f()
    return dec

@adbhook
def adb_connect():
    """check if adb if connect and root"""
    def connect():
        run_sh_command('adb disconnect ' + option.serialno)
        time.sleep(1)
        logging.debug("connect %s" %option.serialno)
        run_sh_command('adb connect ' + option.serialno)
        time.sleep(2)
        logging.debug("root %s" %option.serialno)
        run_sh_command('adb -s %s root' %option.serialno)
        time.sleep(2)
        run_sh_command('adb connect ' + option.serialno)
        time.sleep(2)
        logging.debug("remount %s" %option.serialno)
        run_sh_command('adb -s %s remount' %option.serialno)

    if option.serialno == None:
        devices = run_sh_command('adb devices').split(os.linesep)
        device = devices[1: len(devices)-2]
        if len(device) == 0:
            raise AdbException("no device connected")
        if len(device) == 1:
            option.serialno = device[0].split('\t')[0]
            logging.debug("device is %s" %option.serialno)
        else:
            raise AdbException("more than one device connected")

    if '.' in option.serialno:
        _retry_time = 5
        s=run_sh_command("adb connect "+option.serialno)
        s = s.split(os.linesep)
        if 'unable to connect to' in s[0]:
            print "retry connect " + option.serialno
            for i in range(_retry_time):
                connect()
                if 'unable to connect to' not in run_sh_command("adb connect "+option.serialno).split(os.linesep)[0]:
                    break;
    else:
        logging.debug("root %s" %option.serialno)
        s = run_sh_command('adb -s %s root' %option.serialno)
        if 'error:' in s:
            raise AdbException(s)
        time.sleep(2)
        logging.debug("remount %s" %option.serialno)
        r = run_sh_command('adb -s %s remount' %option.serialno)

#@adbhook
def run_adbshell_command(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE):
    """run adb shell command as nohup, return subprocess.Popen instance"""
    adb_command = ['adb', '-s', option.serialno,'shell']
    if not isinstance(cmd, list): cmd = [cmd]
    logging.debug("command: "+str(adb_command+cmd))
    return subprocess.Popen(adb_command+cmd, stdout=stdout,stderr=stderr)

def run_sh_command(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT):
    """run linux shell command, return result or error"""
    p = subprocess.Popen(cmd, stdout=stdout,stderr=stderr, shell=True)
    result = p.communicate()
    return result[0]

def createLogDir(reportdir):
    logdirlist = []
    ret = '0'
    for f in os.listdir(reportdir):
        if os.path.isdir(os.path.join(reportdir,f)):
            logdirlist.append(f)
    if logdirlist == []:
        return ret
    intlogdir = [int(x) for x in logdirlist]
    intlogdir.sort()
    ret = intlogdir.pop()
    try:
        ret = str(ret+1)
    except Exception, e:
        ret = ret+"_0"
    return ret

def captureResult(filename):
    """analyze uiautomator log
        return a tuple as (result, info)
        result: PASS or FAIL
        info: [] if PASS otherwise failed info
    """
    result = "ERROR"
    runtime = ""
    uilog = []
    with open(filename, "rb+") as fp:
        for line in fp:
            # line = line.split('\r\n')
            l = line.strip()
            if l:
                uilog.append(l)
    for i in range(len(uilog)):
        if uilog[i].startswith("Time:"):
            runtime = uilog[i].strip().split(":")[1]
            if i== len(uilog)-1:
                result = 'PASS'
            else:
                if uilog[i+1].startswith("OK"):
                    result = 'PASS'
                else:
                    result = 'FAIL'
    info = []
    for line in uilog:
        if line.startswith('INSTRUMENTATION_STATUS: stack='):
            info.append(line)
        if line.startswith("INSTRUMENTATION_STATUS: fail file"):
            info.append(line)
    return result, runtime, info

def HtmlReport(suitetest, path):
    """generator html report for all testcases """

    TOTAL = 0
    SUCCESS = 0
    FAILED = 0
    ERROR = 0
    for test in suitetest:
        if test.result == "PASS":
            SUCCESS += 1
        elif test.result == "FAIL":
            FAILED += 1
        elif test.result == "ERROR":
            ERROR += 1
    TOTAL = len(suitetest)
    PRODUCT = run_sh_command('adb -s %s shell getprop ro.build.product' %option.serialno)
    VERSION = run_sh_command('adb -s %s shell getprop ro.build.description' %option.serialno)

    f = open(os.path.join(path, 'index.html'), 'w')
    try:
        def output(s):
            f.write(s + '\n')
            s = re.sub(r'<.*?>', '', s)
            if s != '': print (s)
        output('<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />')
#output('<style>')
#       output('table{ background:#aaa;}')
#       output('table tr td{ background:#fff;}')
#       output('</style>')

        output('<table width="650" border="0" >')
        output('<tr style="background-color:PowderBlue;text-align:center;"><td colspan="2"><h1>AutoSmoke Summary Result</h1></td></tr>')
        output('<tr style="background-color:PowderBlue;"><td><h3>Product</h3></td><td><h3>%s</h3></td></tr>'%PRODUCT)
        output('<tr style="background-color:PowderBlue;"><td><h3>Version</h3></td><td><h3>%s</h3></td></tr>'%VERSION)
        output('<tr style="background-color:PowderBlue;"><td><h3>Total</h3></td><td><h3>%s</h3></td></tr>'%TOTAL)
        output('<tr style="background-color:green;"><td><h3>Pass</h3></td><td><h3>%s</h3></td></td></tr>'%SUCCESS)
        output('<tr style="background-color:red;"><td><h3>Fail</h3></td><td><h3>%s</h3></td></tr>'%FAILED)
        output('<tr style="background-color:yellow;"><td><h3>Error</h3></td><td><h3>%s</h3></td></tr>'%ERROR)
        output('</table>')
        output('<br />')

        """
        try:
            import pygal
            pie_chart = pygal.Pie(width=800, height=400, print_values=True, print_zeroes=True)
            pie_chart.title = 'All Running Case Result Summary (in %)'
            pie_chart.add("PASS", SUCCESS)
            pie_chart.add("FAIL", FAILED)
            pie_chart.add("ERROR", ERROR)
            pie_chart.value_formatter = lambda x: "%.15f" % x
            pie_chart.render_to_file(os.path.join(path,"overload.svg"))
            #use width and height to zoom picture
            output('<iframe src="overload.svg" width="800" height="400">')
            output('</iframe>')
        except Exception, e:
            print "import pygal error"
            print e
        """

        output('<table heigh="500" width="800" border="0">')
        output('<tr style="background-color:PowderBlue;text-align:center;"><td colspan="4"><h1>AutoSmoke Detail Result</h1></td></tr>')
        output('<tr style="background-color:PowderBlue;">')
        output('<td><h3>%5s</h3></td> <td><h3>%-80s</h3></td> <td><h3>%-10s</h3></td> <td><h3>%-6s</h3></td>' %
            ('ID', 'TEST NAME', 'EXECUTE TIME', 'RESULT'))
        output('</tr>')
        for s in suitetest:
            output('<tr style="background-color:PowderBlue;height:40px;">')
            output('<td>%05s</td> <td><a href="%s">%-80s</a></td> <td>%-10s</td> <td><a href="%s">%s</a></td>' %(
                os.path.basename(s.logDirectory), os.path.join(s.logDirectory, UI_AUTOMATOR_LOG), ','.join(s.names), s.runtime, s.logDirectory, s.result
                ))
            output('</tr>')

            #display
            if os.path.exists(os.path.join(s.resultDirectory, s.logDirectory, "display.txt")):
                output('<tr style="background-color:#EE7600">')
                output('<td colspan="4">')
                with open(os.path.join(s.resultDirectory, s.logDirectory, "display.txt")) as fp:
                    for line in fp:
                        output("<div>"+line+"</div>")
                output("</td>")
                output("</tr>")
            if s.errorinfo != "":
                output('<tr style="background-color:#EE7600">')
                output('<td colspan="4">')
                for line in s.errorinfo:
                    output("<div>"+line+"</div>")
                output("</td>")
                output("</tr>")

        output('</table>')

    except Exception, e:
        print e
    finally:
        f.close()

PIC_SHELL_PATH = "/data/local/tmp/hometest"
LOGCAT_RUNTEST = [('logcat -c;logcat -v threadtime', 'logcat_main.txt'), ('cat /proc/kmsg', 'kmsg.txt'), ('dumpsys meminfo', '../dumpsys_meminfo.txt')]
UI_AUTOMATOR_LOG = "caselog.txt"
def prepare():
    """do sth before test before
        such as:
            1. create logging directory
            2. catpure logcat, kmesg
    """
    # check if another uiautomator case is running
    uiautomatorPs = run_sh_command('adb -s %s shell ps| grep uiautomator' %option.serialno)
    if uiautomatorPs != "":
        ps = re.compile(r'\s+').split(uiautomatorPs)[1]
        print "Kill Another UiAutomator Case[%s]" %ps
        run_sh_command('adb -s %s shell kill %s' %(option.serialno, ps))

    global report, resultDirectory, logDirectory
    if 'report' not in globals().keys():
        report = time.strftime("%Y_%m_%d.%H_%M_%S",time.localtime(time.time()))
    # resultDirectory = os.path.join(os.path.dirname(os.path.abspath(__file__)), option.reportdir, 'logs', 'result.%s' %report)
    resultDirectory = os.path.join(option.reportdir, "logs", 'result.%s' %report)
    if not os.path.exists(resultDirectory): os.makedirs(resultDirectory)
    logDirectory = createLogDir(resultDirectory)
    if not os.path.exists(os.path.join(resultDirectory, logDirectory)): os.makedirs(os.path.join(resultDirectory, logDirectory))
    global running_process
    running_process = [run_adbshell_command(command,stdout=open(os.path.join(resultDirectory,logDirectory,filename), "a+")) for command, filename in LOGCAT_RUNTEST]
    run_adbshell_command("rm /data/local/tmp/hometest/*.png")

def teardown():
    """ do sth after test!
        run after prepare()
    """
    s = run_sh_command('adb -s %s shell ls %s' %(option.serialno, PIC_SHELL_PATH))
    if s != "":
        for pic in s.split('\r\n'):
            run_sh_command('adb -s %s pull %s/%s %s/' %(option.serialno, PIC_SHELL_PATH,pic,os.path.join(globals().get("resultDirectory"),globals().get("logDirectory"))))

    for p in globals().get('running_process', []):
        if isinstance(p, subprocess.Popen):
            p.kill()


def run(test):
    """ run single TestCase"""
    prepare()
    test.logDirectory = globals().get('logDirectory')
    test.resultDirectory = globals().get("resultDirectory")
    logging.debug(test.resultDirectory)
    logging.debug(test.logDirectory)
    caselog = os.path.join(test.resultDirectory,test.logDirectory,UI_AUTOMATOR_LOG)
    print "running: %s" %(test.uicommand())
    runtest = run_adbshell_command("uiautomator runtest %s" %(test.uicommand()),stdout=open(caselog,"a+"))
    runtest.wait()
    """
    runtest = run_adbshell_command("uiautomator runtest %s" %(test.uicommand()))#,stdout=open(caselog,"a+"))
    while runtest.poll() == None:
        line = runtest.stdout.readline()
        print line.strip()
        with open(caselog, "a+") as fp:
            fp.write(line)
    """
    result, runtime, info = captureResult(caselog)
    print result,"\n"
    test.result = result
    test.runtime = runtime
    if info != []:test.errorinfo = info
    teardown()

    #operate display message
    c = open("display.py", "rt").read()
    exec(compile(c, "display.py",'exec'), globals(), locals())

def runTests(listfile, count):
    suite = TestSuite()
    if listfile != None:
        for i in range(count):
            if os.path.isfile(listfile):
                suite.loadTestFromFile(listfile)
                # for test in suite.loadTestFromFile(listfile):
                #     run(test)
            else:
                suite.loadTestFromName(listfile)
                # run(suite.loadTestFromName(listfile))
    else:
        raise AdbException("Input Error: -f " + listfile)

    for test in suite.test:
        run(test)

    HtmlReport(suite.test, globals().get('resultDirectory'))
    print "\nreport directory: ", globals().get('resultDirectory')

def pushjar(device, jar):
    r = run_sh_command("adb -s %s push %s /data/local/tmp/" %(device, jar))
    try_time = 1
    while not re.compile(r'\d+ KB/s.*').match(r) and try_time <= 10:
        print "try to push %s: %d" %(jar,try_time)
        r = run_sh_command("adb -s %s push %s /data/local/tmp/" %(device, jar))
        try_time += 1
    if not re.compile(r'\d+ KB/s.*').match(r):
        raise AdbException("fail to push %s" %jar)

def main():
    parse = OptionParser()
    parse.add_option('-f', '--file', dest='listfile', help='case or list to run', action='store')
    parse.add_option('-s', '--serial', dest='serialno', help='which device to run', action='store')
    parse.add_option('-c', '--count', dest='count', help='how many times to run', action='store', default='1')
    parse.add_option('-r', '--reportdir', dest='reportdir', help='where to capture report', action='store', default=".")
    parse.add_option('-j', '--jar', dest='jarpath', help='which jar to run', action='store', default="./smoke.jar")
    global option
    (option, args) = parse.parse_args()
    adb_connect()
    pushjar(option.serialno, option.jarpath)

    count = int(option.count)

    runTests(option.listfile, count)
    # for times in range(1, count+1):
    #     print "\n","*"*30+" START LOOP %d "%times+"*"*30
    #     runTests(option.listfile)



if __name__ == '__main__':
    main()

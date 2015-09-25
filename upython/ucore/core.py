#coding=utf-8
import os
import re
import time
import threading
import subprocess
from optparse import OptionParser

import log
from case import TestCase
from case import TestSuite
from connect import ADB, AdbException


def hook(c):
    def decorator(f):
        setattr(c, f.__name__, f)
        return f
    return decorator

LOGCAT_RUNTEST = [  ('logcat -c;logcat -v threadtime', log.logcat()),
                    ('cat /proc/kmsg', log.kernel()),
                    ('dumpsys meminfo', log.dumpsys_meminfo()),
                    ('procrank', log.procrank()),]

CAPTURE_MEMINFO_SLEEP_GAP = 10

class TextRunner(object):

    def __init__(self, a, option):
        self.a = a
        self.option = option
        self.test_number = 0
        self.report_dir = os.path.join(option.reportdir, 'logs', 'report.%s'%time.strftime("%Y_%m_%d.%H_%M_%S",time.localtime(time.time())))

        @hook(log)
        def report_directory():
            return report_dir
        try:
            os.makedirs(self.report_dir)
        except:
            pass

        try:
            have_procrank = self.a.adbshell('procrank')
            if 'not found' in have_procrank:
                self.a.adb('push tools/procrank /system/xbin/')
                self.a.adbshell('chomd 777 /system/xbin/procrank')
        except:
            log.error('fail to push procrank')

    def startTest(self, test):
        self.test_number += 1
        test.logDirectory = '%03d' %self.test_number
        try:
            os.mkdir(os.path.join(self.report_dir, test.logDirectory))
        except:
            log.error('mkdir log directory (%s) failed' %os.path.join(self.report_dir, test.logDirectory))

        self.clearLog()
        self.running_process = [self.a.popen(command,stdout=open(os.path.join(os.path.join(self.report_dir, test.logDirectory),filename), "a+")) for command, filename in LOGCAT_RUNTEST]
        print "running: %s" %(test.uicommand())
        runner = self.a.popen("uiautomator runtest %s" %(test.uicommand()),stdout=open(os.path.join(os.path.join(self.report_dir, test.logDirectory), log.uiautomator()),"a+"))
        runner.wait()
        result, runtime, info, output = self.__captureResult(os.path.join(os.path.join(self.report_dir, test.logDirectory), log.uiautomator()))
        print result,"\n"
        test.result = result
        test.runtime = runtime
        test.output += output
        if info != []:test.errorinfo = info

        self.__stopTest(test)
        self.__exec('display.py')

    def __stopTest(self, test):
        for p in self.running_process:
            if isinstance(p, subprocess.Popen):
                p.kill()
        self.getLog(os.path.join(self.report_dir, test.logDirectory))

    def clearLog(self):
        def isExists(filename):
            ishave = self.a.adbshell('ls %s' %filename)
            if 'No such file or directory' in str(ishave):
                return False
            else:
                return True
        if(isExists('/data/anr')):
            log.debug('rm -rf /data/anr')
            self.a.adbshell('rm -rf /data/anr')
        if(isExists('/data/tombstones/tombstone_0*')):
            tbs = self.a.adbshell('/data/tombstones/tombstone_0*')
            for tombstone in tbs.splitlines():
                log.debug('rm %s' %tombstone)
                self.a.adbshell('rm %s' %tombstone)
        self.a.adbshell('rm %s/*.png' %log.save_pic_path())

    def getLog(self, path):
        def isExists(filename):
            ishave = self.a.adbshell('ls %s' %filename)
            if 'No such file or directory' in str(ishave):
                return False
            else:
                return True
        if(isExists('/data/anr')):
            os.mkdir(os.path.join(path, 'anr'))
            self.a.adb('pull /data/anr %s' %os.path.join(path, 'anr'))
        if(isExists('/data/tombstones/tombstone_0*')):
            os.mkdir(os.path.join(path, 'tombstones'))
            self.a.adb('pull /data/tombstones %s' %os.path.join(path, 'tombstones'))

        s = self.a.adbshell('ls %s' %(log.save_pic_path()))
        if s != "":
            for pic in s.splitlines():
                self.a.adb('pull %s/%s %s/' %(log.save_pic_path(), pic, path))

    def __exec(self, pyfile):
        try:
            log.debug('load extend python code file: %s' %pyfile)
            c = open(pyfile, "rt").read()
            exec(compile(c, pyfile,'exec'), globals(), locals())
        except Exception, e:
            log.debug(str(e))

    def startSuite(self, suite):
        #
        # add capture meminfo such as `procrank`, `dumpsys meminfo`, `cat /proc/meminfo`, `promen pid` here
        # do not block anything
        #
        self.__flag = True
        t = threading.Thread(target=self.catMeminfo)
        t.setDaemon(True)
        t.start()
        for test in suite.tests:
            self.startTest(test)

        self.__flag = False

    def __captureResult(self, filename):
        """analyze uiautomator log
            return a tuple as (result, info)
            result: PASS or FAIL
            info: [] if PASS otherwise failed info
            output: [] if PASS otherwise output info
        """
        result = "ERROR"
        runtime = "0.000"
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
        output = []
        for i in range(len(uilog)):
            if uilog[i].startswith('INSTRUMENTATION_STATUS: stack='):
                info.append(uilog[i])
            if uilog[i].startswith("INSTRUMENTATION_STATUS: fail file"):
                info.append(uilog[i])
            if uilog[i].startswith('INSTRUMENTATION_STATUS_CODE: 15'):
                output.append(uilog[i-1].split("=")[1])

        for line in uilog:
            if line.startswith('INSTRUMENTATION_STATUS: stack='):
                info.append(line)
            if line.startswith("INSTRUMENTATION_STATUS: fail file"):
                info.append(line)
        return result, runtime, info, output

    def catMeminfo(self):
        while self.__flag:
            self.a.popen('procrank', stdout=open(os.path.join(self.report_dir, log.procrank()), 'a+'))
            self.a.popen('dumpsys meminfo', stdout=open(os.path.join(self.report_dir, log.dumpsys_meminfo()), 'a+'))
            self.a.popen('cat /proc/meminfo', stdout=open(os.path.join(self.report_dir, log.meminfo()), 'a+'))
            self.a.popen('busybox top', stdout=open(os.path.join(self.report_dir, log.top()), 'a+'))
            time.sleep(10)



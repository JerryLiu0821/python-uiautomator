#coding=utf-8
import os

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
        self.output = []
        self.errorinfo = ""
        self.runtime = ""
        self.descriptive = ""
        self.logDirectory = None

    def uicommand(self):
        """return a uiautomator string command """
        uicmd = self.jar
        for line in self.names:
            uicmd = uicmd + " " + "-c " + line
        return uicmd

class TestSuite():
    def __init__(self):
        self.tests = []

    def __loadTestFromName(self, name):
        """ add single TestCase instance """
        case = self._convertCastList(name)
        test = TestCase(case[0], case[1])
        self.tests.append(test)

    def __loadTestFromFile(self, filename):
        """ add TestCase list for all case in given file """
        with open(filename, "r+") as fp:
            for line in fp:
                line = line.strip()
                if line != "" and not line.startswith("#"):
                    self.__loadTestFromName(line)

    def addTestCase(self, caselist):
        if os.path.isfile(caselist):
            self.__loadTestFromFile(caselist)
        else:
            self.__loadTestFromName(caselist)

    def _convertCastList(self, casestr):
        """return a tuple contain jar, and castlist"""
        castlist = []
        if casestr == "":
            raise Exception("no case found")
        names = casestr.split(",")
        for name in names:
            castlist.append(name.split(".", 1)[1])
        return names[0].split(".", 1)[0], castlist

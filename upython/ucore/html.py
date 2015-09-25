#coding=utf-8
import os
import sys
import re
import log

def HtmlReport(suitetest, dictt):
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
    VERSION = dictt.get('version')
    PRODUCT = dictt.get('product')

    f = open(os.path.join(dictt.get('runner').report_dir, 'index.html'), 'w')
    try:
        def output(s):
            f.write(s + '\n')
            s = re.sub(r'<.*?>', '', s)
            #if s != '': print (s)
        output('<html>')
        output('<head>')
        output('<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />')
        output('<style type="text/css">')
        output('html{background:#D2D460;text-align:center;}')
        output('body{width:800px;margin:0 auto;background:#fff;text-align:left;}')
        output('.summary {width:650px; float:left;}')
        output('.meminfo {width:150px; float:left; margin-right:-150px;}')
        output('</style>')
        output('</head>')

        output('<body>')
        output('<div class="summary">')
        output('<table width="650" border="0" >')
        output('<tr style="background-color:PowderBlue;text-align:center;"><td colspan="2"><h1>AutoSmoke Summary Result</h1></td></tr>')
        output('<tr style="background-color:PowderBlue;"><td><h3>Product</h3></td><td><h3>%s</h3></td></tr>'%PRODUCT)
        output('<tr style="background-color:PowderBlue;"><td><h3>Version</h3></td><td><h3>%s</h3></td></tr>'%VERSION)
        output('<tr style="background-color:PowderBlue;"><td><h3>Total</h3></td><td><h3>%s</h3></td></tr>'%TOTAL)
        output('<tr style="background-color:green;"><td><h3>Pass</h3></td><td><h3>%s</h3></td></td></tr>'%SUCCESS)
        output('<tr style="background-color:red;"><td><h3>Fail</h3></td><td><h3>%s</h3></td></tr>'%FAILED)
        output('<tr style="background-color:yellow;"><td><h3>Error</h3></td><td><h3>%s</h3></td></tr>'%ERROR)
        output('</table>')
        output('</div>')

        output('<div class="meminfo">')
        output('<br/><br/><br/><br/>')
        output('<h3>内存信息:</h3>')
        output('<a href="%s">Total_Pss</a><br/><br/>' %log.total_pss())
        output('<a href="%s">Top_10_Pss</a>' %log.top_10_pss())
        output('</div>')


        output('<br />')

        output('<table heigh="500" width="800" border="0">')
        output('<tr style="background-color:PowderBlue;text-align:center;"><td colspan="4"><h1>AutoSmoke Detail Result</h1></td></tr>')
        output('<tr style="background-color:PowderBlue;">')
        output('<td><h3>%5s</h3></td> <td><h3>%-80s</h3></td> <td><h3>%-10s</h3></td> <td><h3>%-6s</h3></td>' %
            ('ID', 'TEST NAME', 'EXECUTE TIME', 'RESULT'))
        output('</tr>')
        for s in suitetest:
            output('<tr style="background-color:PowderBlue;height:40px;">')
            output('<td>%05s</td> <td><a href="%s">%-80s</a></td> <td>%-10s</td> <td><a href="%s">%s</a></td>' %(
                os.path.basename(s.logDirectory), os.path.join(s.logDirectory, log.uiautomator()), ','.join(s.names), s.runtime, s.logDirectory, s.result
                ))
            output('</tr>')

            """
            #display
            if os.path.exists(os.path.join(s.resultDirectory, s.logDirectory, "display.txt")):
                output('<tr style="background-color:#EE7600">')
                output('<td colspan="4">')
                with open(os.path.join(s.resultDirectory, s.logDirectory, "display.txt")) as fp:
                    for line in fp:
                        output("<div>"+line+"</div>")
                output("</td>")
                output("</tr>")
            """

            if s.output != []:
                output('<tr style="background-color:#EE7600">')
                output('<td colspan="4">')
                for line in s.output:
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
        output('</body>')
        output('</html>')

    except Exception, e:
        print e
    finally:
        f.close()

    d = draw(dictt.get('runner').report_dir)
    d.draw_line()


class draw(object):
    def __init__(self,path):
        self.path = path
        self.procrank = os.path.join(path,log.procrank())
        if not os.path.exists(self.procrank):
            return
        else:
            os.system("dos2unix %s" %self.procrank)

    def list_Pss(self, processname):
        total_pss = []
        with open(self.procrank, "r") as fp:
            for line in fp:
                match_pss = re.compile(r'.*\s+(\d+)K\s+\d+K\s+%s$' %processname).match(line)
                if match_pss:
                    o = match_pss.group(1)
                    total_pss.append(int(o))
        #print processname+": ",total_pss
        return total_pss

    def getTop(self):
        with open(self.procrank, "r") as fp:
            all_lines = fp.readlines()
            lines = []
            times = 0
            for i in range(len(all_lines)):
                m = re.search(r'(\s+PID\s+Vss\s+Rss\s+Pss\s+Uss\s+cmdline)',all_lines[i])
                if m:
                    times += 1
                    for j in range(1, 10):
                        lines.append(all_lines[i+j])
            pname=[]
            for line in lines:
                m = re.search(r'(?P<PID>\d+)\s+(?P<Vss>\d+K)\s+(?P<Rss>\d+K)\s+(?P<Pss>\d+K)\s+(?P<Uss>\d+K)\s+(?P<Pname>\S+)',line)
                if m:
                    pname.append(m.groupdict()['Pname'])

            max=0
            l = list(set(pname))
            return l
            """
            for each in list(set(pname)):
                length = 0
                for i in all_lines:
                    m = re.search(r'(?P<PID>\d+)\s+(?P<Vss>\d+)K\s+(?P<Rss>\d+)K\s+(?P<Pss>\d+)K\s+(?P<Uss>\d+)K\s+(?P<Pname>%s$)' %each,i)
                    if m:
                        if int(m.groupdict()['Pss'])>max:
                            max = int(m.groupdict()['Pss'])
                        length += 1
                if length < times:
                    l.remove(each)
            #l.append(times)
            #l.append(max)
            return l
            """

    def draw_line(self):
        try:
            sys.path.append(os.path.dirname(__file__))
            import pygal
        except Exception, e:
            log.error(str(e))
        #draw TOTAL
        total = self.list_Pss("TOTAL")
        length = len(total)
        lchart = pygal.Line()
        lchart.title = "procrank analyze"
        lchart.x_title = "times/(60s)"
        lchart.y_title = "Pss(K)"
        lchart.width = 1200
        lchart.add("TOTAL", total)
        lchart.x_labels = map(str,range(length))
        lchart.render_to_file(os.path.join(self.path,log.total_pss()))
        #draw top 10
        prss = self.getTop()
        #print "process name: ",prss
        achart = pygal.Line()
        achart.title = "procrank analyze"
        achart.x_labels = map(str,range(length))
        achart.x_title = "times/(60s)"
        achart.y_title = "Pss(K)"
        achart.width = 1200
        for p in prss:
            achart.add(p, self.list_Pss(p))
        achart.render_to_file(os.path.join(self.path, log.top_10_pss()))


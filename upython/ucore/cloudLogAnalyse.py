#coding=utf-8

import os,re,time,datetime,threading,commands

class cloudStatus():
    """detect cloud video status"""
    def __init__(self, filename):
        self.filename = filename

    def openFile(self):
        fp = open(self.filename, "r+")
        contents=[]
        try:
            contents = fp.readlines();
            fp.close()
        except Exception, e:
            fp.close()
            print e
        return contents

    def calculatorbak(self, start_str, end_str):
        """
        params: time format like 12-19 17:31:34.166
        return: int mseconds
        """
        def timeToMS(stri):
            stri_a = stri.split(' ')[0]
            stri_b = stri.split(" ")[1]
            M = int(stri_a.split("-")[0].strip())
            d = int(stri_a.split("-")[1].strip())
            h = int(stri_b.split(":")[0])
            m = int(stri_b.split(":")[1])
            s = int(stri_b.split(":")[2].split(".")[0])
            ms = int(stri_b.split(".")[1])
            return ms+s*1000+m*60*1000+h*60*60*1000+d*24*60*60*1000
        return timeToMS(end_str) - timeToMS(start_str)

    def vodHlsPlayProgress(self, product):
        """return vod play progress"""
        def list_during(re_s, re_e, l):
            """return flag, gap
                flag:0: not match any line;1: match start; 2: match end; 3: match start and end"""
            r=[]
            flag = 0
            if l != []:
                for i in l:
                    if re.compile(re_s).match(i):
                        r.append(i)
                        flag += 1
                        break
                for i in l:
                    if re.compile(re_e).match(i):
                        r.append(i)
                        flag += 2
                        break
            if flag == 3:
                print flag,  str(self.calculatorbak(r[0][:18],r[1][:18]))
                return str(self.calculatorbak(r[0][:18],r[1][:18]))+"ms"
            print flag,'error'
            return 'error'

        #
        #key_down = r'.*injectKeyEvent:\ KeyEvent\ \{\ action=ACTION_DOWN,\ keyCode=KEYCODE_DPAD_CENTER.*'
        #user_press = r'.*LETVPlay:\ jumpToPlay\s*$'
        #tvban_get_url = r'.*LinkShellUtil:\ getURLFromLink\ outPut:(.*$)'
        player_get_url = r'.*MediaPlayerService.*setDataSource\((\S+)\)'
        #player_post_m3u8 = r'.*DataSource_M3U8.*:\ \[parseURLs\]\ try\ parseURLs=(\S+)'
        #utp_get_first_request = r'.*\[utp_play_handler\]\ handle_request\ 127\.0\.0\.1:\d+\ \ /play?.*'
        #utp_request_download_url = r'.*\[downloader\]\ start_download\ http_range:bytes=-\ http://g3\.letv\.cn/vod.*'
        #utp_download_first_m3u8 = r'.*\[downloader\]\ start_download\ http_range:bytes=-\ http://.*/.*\.m3u8\?.*'
        #utp_start_download_first_slice = r'.*\[downloader\]\ start_download\ http_range:bytes=0-\d+ (.*)'
        #utp_finish_download_first_slice = r'.*\[downloader\]\ on_http_complete.*'
        #player_finish_parser_m3u8 = r'.*\[init\]\ parseURLs\ Success!\ urlNum\ :\ 3'
        player_post_first_ts_slice = r'.*PlaylistFetcher.*fetching.*'
        #init_video = r'.*Creating\ Video\ Decoder\ video/avc'
        #init_video_end = r'.*Video\ Decoder\ instantiante\ end'
        #init_audio = r'.*Creating\ Audio\ Decoder\ audio.*'
        #init_audio_end = r'.*Audio\ Decoder\ instantiante\ end'
        if product == "max1":
            player_prepared =r'.*MediaPlayerService.*:\ \[(\d+)\]\ notify\ \(\w+,\ 1,\ 0,\ 0\)'
            player_start = r'.*MediaPlayerService.*:\ \[(\d+)\]\ start\s*$'
            first_frame = r'.*MediaPlayerService.*:\ \[(\d+)\]\ notify\ \(\w+,\ 200,\ 3,\ 0\)'
            reset = r'.*MediaPlayerService.*:\ \[(\d+)\]\ reset\s*$'
            reset_done = r'.*MediaPlayerService.*:\ \[(\d+)\]\ reset\ done\s*$'
        if product == 'x600':
            player_prepared =r'.*MediaPlayerService.*: \[notify\] \[(\d+)\]\ notify\ \(\w+,\ 1,\ 0,\ 0,\ 0\)'
            player_start = r'.*MediaPlayerService.*: \[notify\] \[(\d+)\]\ notify\ \(\w+,\ 6,\ 0,\ 0,\ 0\)'
            first_frame = r'.*MediaPlayerService.*: \[notify\] \[(\d+)\]\ notify\ \(\w+,\ 200,\ 3,\ 0,\ 0\)'
            reset = r'.*MediaPlayerService.*: \[reset\] \[(\d+)\]\ reset\s*$'
            reset_done = r'.*MediaPlayerService.*: \[~Client\] \[(\d+)\]~Client\s*$'


        #after user_press
        #regex = [user_press,tvban_get_url,player_get_url,player_post_m3u8,init_video,init_video_end,init_audio,init_audio_end,player_prepared,player_start,first_frame]
        regex = [player_get_url,player_prepared,player_start,first_frame,reset,reset_done]
        #after utp_get_first_request
        #utp_finish_download_first_slice url must match utp_start_download_first_slice
        #regex_first = [utp_get_first_request,utp_request_download_url, utp_download_first_m3u8, utp_start_download_first_slice, player_finish_parser_m3u8, player_post_first_ts_slice]
        regex_first = [player_post_first_ts_slice]

        rr = "|".join(regex)

        progress = []
        logcontents = self.openFile()
        if logcontents == []:
            print 'logcat is null'
            return []

        index = 0;
        for i in range(len(logcontents)):
            if re.compile(player_get_url).match(logcontents[i]):
                index = i

        for line in logcontents[index:]:
            if re.compile(rr).match(line):
                progress.append(line)
        for line in logcontents[index:]:
            for i in regex_first:
                if re.compile(i).match(line):
                    progress.append(line)
                    regex_first.remove(i)
                    break

        """
        #find user press
        index = 0
        for line in logcontents:
            if re.compile(user_press).match(line):
                index = logcontents.index(line)
                break
        for line in logcontents[index:]:
            if re.compile(rr).match(line):
                progress.append(line)

        #only one utp_get_first_request after user press
        utp_index = 0
        for line in logcontents[index:]:
            if re.compile(utp_get_first_request).match(line):
                utp_index = logcontents.index(line)
                break

        for line in logcontents[utp_index:]:
            for i in regex_first:
                if re.compile(i).match(line):
                    progress.append(line)
                    regex_first.remove(i)
                    break

        #utp_finish_download_first_slice to match url from utp_start_download_first_slice
        for line in logcontents[utp_index:]:
            match = re.compile(utp_start_download_first_slice).match(line)
            if match:
                url = match.group(1)
                i = logcontents.index(line)
                for l in logcontents[i:]:
                    if url in l and "on_http_complete" in l:
                        progress.append(l)
                        break
                break
        """
        progress.sort()
        print "progress:",len(progress)
        #for i in progress: print i
        result = []

        """
        # init V/A
        av = []
        for i in progress:
            if re.compile("|".join([init_video,init_video_end,init_audio,init_audio_end])).match(i):
                av.append(i)
        av.sort()

        progress.remove(av[1])
        progress.remove(av[2])
        # end init V/A
        """
        for i in progress: print i
        result.append("player_get_url -> first_frame: " + list_during(player_get_url,first_frame,progress))
        result.append("player_get_url -> player_post_first_ts_slice: " + list_during(player_get_url,player_post_first_ts_slice,progress))
        result.append("player_post_first_ts_slice -> player_prepared: " + list_during(player_post_first_ts_slice,player_prepared,progress))
        result.append("player_prepared -> player_start: " + list_during(player_prepared,player_start,progress))
        result.append("player_start -> first_frame: " + list_during(player_start,first_frame,progress))
        result.append("reset -> reset_done: " + list_during(reset,reset_done,progress))

        return result

class adbLogcatThread(threading.Thread):
    def __init__(self,filename):
        threading.Thread.__init__(self)
        self.filename = filename
        self.flag = True
    def run(self):
        while self.flag:
            os.system("adb logcat -c")
            os.system("adb logcat -v time > %s" %self.filename)
    def stop(self):
        self.flag = False
        ps = commands.getoutput('ps aux | grep "adb logcat -v time$"')
        os.system("kill -9 %s" %ps.split(" ")[4])


if __name__ == "__main__":
    alt = adbLogcatThread("aaa.txt")
    alt.setDaemon(True)
    alt.start()
    time.sleep(5)
    alt.stop()

    vodlist = ['http://10.154.250.32:8080/live/cloudvideo_function/hls/720P/desc.m3u8',

    ]
    for each in vodlist:
        print "start: %s" %each
        log = each.split("/")
        log = "_".join(log[-3:])
        log = log+".txt"
        alt = adbLogcatThread(log)
        alt.setDaemon(True)
        alt.start()
        cmd = 'am start -d "%s" -n com.android.gallery3d/.app.MovieActivity' %each
        os.system("adb shell "+cmd)
        time.sleep(20)
        os.system("adb shell input keyevent 4")
        time.sleep(2)
        alt.stop()
        c = cloudStatus(log)
        c.vodHlsPlayProgress()

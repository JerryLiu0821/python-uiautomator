import os,re,time
import datetime

class cloudStatus():
    """detect cloud video status"""
    def __init__(self, filename):
        self.filename = filename

    def playerError(self):
        """return MediaPlayer Error times"""
        logcontents = self.openFile()
        p = re.compile(r'MediaPlayer: error')
        result = 0
        if logcontents != []:
            for line in logcontents:
                if p.search(line):
                    result += 1
        else:
            print self.filename + " is null"
        print "MediaPlayer: error:  %s" %result
        return result

    def getUtpVersion(self):
        """return utp version"""
        logcontents = self.openFile()
        p = re.compile(r'\[UTPModule\]\ utp\ status:\ (.*)\ .*')
        duration = -1
        if logcontents !=[]:
            for line in logcontents:
                match = p.search(line)
                if match:
                    duration = match.group(1)
        return duration

    def getPlayDuration(self):
        """return play duration"""
        logcontents = self.openFile()
        p = re.compile(r'MediaPlayerService.*: \[\d+\] getDuration = (\d+)')
        duration = -1
        if logcontents !=[]:
            for line in logcontents:
                match = p.search(line)
                if match:
                    duration = match.group(1)
        print "duration: %s" %duration
        return duration

    def getResolution(self):
        """return resolution"""
        logcontents = self.openFile()
#MediaPlayerService( 1232): [42] notify (0x40076db0, 5, 640, 352)
#MediaPlayerService: [33] notify (0x4e4fbe30, 5, 1280, 720)
#MediaPlayerService: [27] notify (0x539209a0, 5, 1280, 720)
        p = re.compile(r'.*MediaPlayerService.*:\ \[\d+\]\ notify\ \(\w+,\ 5,\ (\d+),\ (\d+)\)\s*')
        resolution = ""
        if logcontents !=[]:
            for line in logcontents:
                match = p.match(line)
                if match:
                    resolution = match.group(1)+"*"+match.group(2)
                    break
        print "Resolution: %s" %resolution
        return resolution

    def checkVodStopStatus(self):
        """return exit player correct or wrong"""
        isExit = False
        logcontents = self.openFile()
        allstatus = []
        stop = r'.*MediaPlayerService.*: \[(\d+)\] stop\s*$'
        stop_done = r'.*MediaPlayerService.*: \[\d+\] stop done\s*$'
        disconnect = r'.*MediaPlayerService.*: disconnect\(\d+\) from pid \d+\s*$'
        disconnect_done= r'.*MediaPlayerService.*: \[\d+\] disconnect done\s*$'
        if logcontents != []:
            for i in range(len(logcontents)):
                if re.compile("|".join([stop,stop_done,disconnect,disconnect_done])).match(logcontents[i]):
                    allstatus.append(str(i)+" "+logcontents[i])

        if allstatus != []:
            allstatus.sort()
            #for i in allstatus:print i
        else:
            print "stop progress is null"
            return isExit
        i=0
        while (i < len(allstatus)):
            if re.compile(stop).match(allstatus[i]):
                flag = 1
                pipe = re.compile(stop).match(allstatus[i]).group(1)
                for j in range(i+1,len(allstatus)):
                    if re.compile(r'.*MediaPlayerService.*: \[%s\] stop done\s*$' %pipe).match(allstatus[j]):
                        flag += 1
                        i = j+1
                        for k in range(j+1, len(allstatus)):
                            if re.compile(r'.*MediaPlayerService.*: disconnect\(%s\) from pid \d+\s*$' %pipe).match(allstatus[k]):
                                flag += 1
                                i=k+1
                                for m in range(k+1, len(allstatus)):
                                     if re.compile(r'.*MediaPlayerService.*: \[%s\] disconnect done\s+$' %pipe).match(allstatus[m]):
                                         flag += 1
                                         i = k+1
                                         break
                                break
                        break
                    else:
                        i += 1
                if flag != 4:
                    print "exit player error %s" %pipe
                    isExit = False
                else:
                    isExit = True
                    print "exit corrected %s" %pipe

            else:
                i += 1

        return isExit

    def checkVodPlayStatus(self):
        """return playing is incremental or not"""
        incremental = True
        logcontents = self.openFile()
        positions = []
        p = re.compile(r'.*MediaPlayerService.*: \[\d+\] getCurrentPosition = (\d+)\s+$')
        if logcontents != []:
            for line in logcontents:
                match = p.match(line)
                if match:
                    positions.append(int(match.group(1)))

        org = copy.copy(positions)
        positions.sort()
        return org == positions

    def checkVodPauseStatus(self):
        """return if player is paused or not"""
        logcontents = self.openFile()
        pause = []
        pause_pattern = r'.*VideoPlayer-VideoPlayer.*: onKeyUp keyCode = 23'
        if logcontents != []:
            for i in logcontents:
                if re.compile(pause_pattern).match(i):
                    pause.append(i)
        else:
            print 'logcat is null'
            return False
        if len(pause) == 0:
            print 'not pause'
            return False

        times = len(pause)/2
        print 'pause times: %s' %times
        flag = 0
        if times == 0:
            for j in range(logcontents.index(pause[i-1]), len(logcontents)):
                if re.compile(r'.*MediaPlayerService.*: \[\d+\] getCurrentPosition =\d+$').match(j):
                    flag += 1
                    break
        else:
             for i in range(times):
                 for j in range(logcontents.index(pause[i*2]), logcontents.index(pause[i*2+1])):
                     if re.compile(r'.*MediaPlayerService.*: \[\d+\] getCurrentPosition =\d+$').match(logcontents[j]):
                         flag += 1
                         print 'pause failed'
                         break
        if flag != 0:
            print "player cannot pause"
            return False
        else:
             return True

    def checkVodHlsSeekStatus(self):
        """return seek status"""
        logcontents = self.openFile()
        seek = []
        pseek = r'.*MediaPlayerService.*: \[(\d+)\] seekTo\((\d+)\)\s*$'
        seek_done = r'.*MediaPlayerService.*: \[\d+\] seekTo done\s*$'
        seek_notify = r'.*MediaPlayerService.*: \[\d+\] notify \(\w+, 4, 0, 0\)\s*$'
        position = r'.*MediaPlayerService.*: \[\d+\] getCurrentPosition = (\d+)\s*$'
        if logcontents != []:
            for i in range(len(logcontents)):
                if re.compile("|".join([pseek,seek_done,seek_notify,position])).match(logcontents[i]):
                    seek.append(str(i)+" "+logcontents[i])
        if seek == []:
            print "no seek in %s" %self.filename
        seek.sort()
        ok = True
        i=0
        while(i < len(seek)):
            matchi = re.compile(pseek).match(seek[i])
            if matchi:
                pipe = matchi.group(1)
                seekto = matchi.group(2)
                flag = False
                for j in range(i+1,len(seek)):
                    matchj = re.compile(r'.*MediaPlayerService.*: \[%s\] getCurrentPosition = (\d+)\s*$' %pipe).match(seek[j])
                    if matchj:
                        cposition = matchj.group(1)
                        i = j+1
                        flag = True
                        kd = int(seekto) - int(cposition)
# if the src is hls the kd is 25000, if http the kd is 10000
                        if kd > 25000 or kd < -25000:
                            print "seekTo(%s), getCurrentPosition = %s" %(seekto,cposition)
                            ok = False;
                        break
                if not flag:
                    print "no getCurrentPosition found after seekTo(%s)" %seekto
                    i = len(seek)
            else:
                i += 1
        return ok

    def checkVodHttpSeekStatus(self):
        """return seek status"""
        logcontents = self.openFile()
        seek = []
        pseek = r'.*MediaPlayerService.*: \[(\d+)\] seekTo\((\d+)\)\s*$'
        seek_done = r'.*MediaPlayerService.*: \[\d+\] seekTo done\s*$'
        seek_notify = r'.*MediaPlayerService.*: \[\d+\] notify \(\w+, 4, 0, 0\)\s*$'
        position = r'.*MediaPlayerService.*: \[\d+\] getCurrentPosition = (\d+)\s*$'
        if logcontents != []:
            for i in range(len(logcontents)):
                if re.compile("|".join([pseek,seek_done,seek_notify,position])).match(logcontents[i]):
                    seek.append(str(i)+" "+logcontents[i])
        if seek == []:
            print "no seek in %s" %self.filename
        seek.sort()
        ok = True
        i=0
        while(i < len(seek)):
            matchi = re.compile(pseek).match(seek[i])
            if matchi:
                pipe = matchi.group(1)
                seekto = matchi.group(2)
                flag = False
                for j in range(i+1,len(seek)):
                    matchj = re.compile(r'.*MediaPlayerService.*: \[%s\] getCurrentPosition = (\d+)\s*$' %pipe).match(seek[j])
                    if matchj:
                        cposition = matchj.group(1)
                        i = j+1
                        flag = True
                        kd = int(seekto) - int(cposition)
# if the src is hls the kd is 25000, if http the kd is 10000
                        if kd > 10000 or kd < -10000:
                            print "seekTo(%s), getCurrentPosition = %s" %(seekto,cposition)
                            ok = False;
                        break
                if not flag:
                    print "no getCurrentPosition found after seekTo(%s)" %seekto
                    i = len(seek)
            else:
                i += 1
        return ok

    def livePlayProgress(self):
        """return a progress list """
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
                return str(self.calculatorbak(r[0][:18],r[1][:18]))+"ms"
            print flag
            return 'error'
        user_press = r'.*Launcher.*:\ T2LauncherActivity\ --\ onKeyDown:\ KeyEvent\ \{\ action=ACTION_DOWN,\ keyCode=KEYCODE_CHANNEL_(UP|DOWN).*'
        launcher_get_url = r'.*Launcher.*:\ LivePlayerController\ --\ play\(\)\ -\ uri:(\S+)\ pip:\ false\s*$'
        player_get_url = r'.*MediaPlayerService.*:\ \[(\d+)\]\ setDataSource\((\S+)\)'
#player_prepare = r'.*MediaPlayerService.*:\ \[(\d+)\]\ prepareAsync\s*$'
        player_post_m3u8 = r'.*DataSource_M3U8.*:\ \[parseURLs\]\ try\ parseURLs=(\S+)'
        utp_get_first_request = r'.*\[utp_play_handler\]\ handle_request\ 127\.0\.0\.1:\d+\ \ /play?.*'
        utp_request_download_url = r'.*\[downloader\]\ start_download\ http_range:bytes=-\ http://live\.gslb\.letv\.com/gslb.*'
        utp_download_first_m3u8 = r'.*\[downloader\]\ start_download\ http_range:bytes=-\ http://.*/desc\.m3u8\?.*'
        utp_parser_m3u8_assign_download_task = r'.*\[app\]\ add\ slice.*'
        utp_start_download_first_slice = r'.*\[downloader\]\ start_download\ http_range:bytes=0-\d+\ (.*)'
        utp_finish_download_first_slice = r'.*\[downloader\]\ on_http_complete.*'
        player_finish_parser_m3u8 = r'.*\[init\]\ parseURLs\ Success!\ urlNum\ :\ 3'
        player_post_first_ts_slice = r'.*\[init\]\ \[M3u8\]\ post\ cmd\ for\ start\ first\ url:(\S+)'
        init_video = r'.*Creating\ Video\ Decoder\ video/avc'
        init_video_end = r'.*Video\ Decoder\ instantiante\ end'
        init_audio = r'.*Creating\ Audio\ Decoder\ audio.*'
        init_audio_end = r'.*Audio\ Decoder\ instantiante\ end'
        player_prepared =r'.*MediaPlayerService.*:\ \[(\d+)\]\ notify\ \(\w+,\ 1,\ 0,\ 0\)'
        player_start = r'.*MediaPlayerService.*:\ \[(\d+)\]\ start\s*$'
        first_frame = r'.*MediaPlayerService.*:\ \[(\d+)\]\ notify\ \(\w+,\ 200,\ 3,\ 0\)'

        utp_handle_mirrors = r'.*\[xml_content_parser\]\ handle_mirrors\ http.*'


        regex = [user_press,launcher_get_url,player_get_url,player_post_m3u8,utp_request_download_url,player_finish_parser_m3u8, init_video,init_video_end,init_audio,init_audio_end,player_prepared,player_start,first_frame]
        regex_first = [utp_download_first_m3u8, utp_parser_m3u8_assign_download_task, utp_start_download_first_slice, player_post_first_ts_slice, utp_handle_mirrors]
#regex_first remove utp_get_first_request
#regex_first remove utp_finish_download_first_slice to match url from utp_start_download_first_slice
        len_regex_first = len(regex_first) + 2

        rr = "|".join(regex)

        progress = []
        logcontents = self.openFile()
        print "file length: %d" %len(logcontents)
        index = 0
        last = index
        setDataSourceIndex = 0
        if logcontents != []:
            for line in logcontents:
                if re.compile(user_press).match(line):
                    index = logcontents.index(line)
                    break
            for line in logcontents[index:]:
                if re.compile(first_frame).match(line):
                    last = logcontents.index(line) + 1
                    break
            for line in logcontents[index:]:
                if re.compile(player_get_url).match(line):
                    setDataSourceIndex = logcontents.index(line)
                    break
        else:
            return
        for line in logcontents[index:last]:
            if re.compile(rr).match(line):
                progress.append(line)

        first_request = 0
        for line in logcontents[setDataSourceIndex:last]:
            if re.compile(utp_get_first_request).match(line):
                progress.append(line)
                first_request = logcontents.index(line)
                break
        for line in logcontents[first_request:last]:
            for i in regex_first:
                if re.compile(i).match(line):
                    progress.append(line)
                    regex_first.remove(i)
                    break

        #utp_finish_download_first_slice to match url from utp_start_download_first_slice
        for line in logcontents[first_request:last]:
            match = re.compile(utp_start_download_first_slice).match(line)
            if match:
                url = match.group(1)
                i = logcontents.index(line)
                for l in logcontents[i:]:
                    if url in l and "on_http_complete" in l:
                        progress.append(l)
                        break
                break
        progress.sort()
        print "progress:",len(progress)
        for i in progress: print i
        result = []
        if len(progress) != (len(regex) + len_regex_first):
            print 'length is not matched'
#return result

        # init V/A
        av = []
        for i in progress:
            if re.compile("|".join([init_video,init_video_end,init_audio,init_audio_end])).match(i):
                av.append(i)
        av.sort()
        for i in av: print i

        progress.remove(av[1])
        progress.remove(av[2])
        # end init V/A
        for i in progress: print i

        result.append("user_press -> first_frame: " + str(list_during(user_press,first_frame,progress)))
        result.append("user_press -> launcher_get_url: " + str(list_during(user_press,launcher_get_url,progress)))
        result.append("launcher_get_url -> player_get_url: " + str(list_during(launcher_get_url,player_get_url,progress)))
        result.append("player_get_url -> player_post_m3u8: " + str(list_during(player_get_url,player_post_m3u8,progress)))
#result.append("player_get_url -> player_prepare: " + str(list_during(player_get_url,player_prepare,progress)))
#result.append("player_prepare -> player_post_m3u8: " + str(list_during(player_prepare,player_post_m3u8,progress)))
        result.append("player_post_m3u8 -> utp_get_first_request: " + str(list_during(player_post_m3u8,utp_get_first_request,progress)))
        result.append("utp_get_first_request -> utp_request_download_url: " + str(list_during(utp_get_first_request,utp_request_download_url,progress)))
        result.append("utp_request_download_url -> utp_download_first_m3u8: " + str(list_during(utp_request_download_url,utp_download_first_m3u8,progress)))
        result.append("utp_download_first_m3u8 -> utp_parser_m3u8_assign_download_task: " + str(list_during(utp_download_first_m3u8,utp_parser_m3u8_assign_download_task,progress)))
        result.append("utp_parser_m3u8_assign_download_task -> utp_start_download_first_slice: " + str(list_during(utp_download_first_m3u8,utp_start_download_first_slice,progress)))
        result.append("utp_start_download_first_slice -> utp_finish_download_first_slice: " + str(list_during(utp_start_download_first_slice,utp_finish_download_first_slice,progress)))
        result.append("player_post_m3u8 -> player_finish_parser_m3u8: " + str(list_during(player_post_m3u8,player_finish_parser_m3u8,progress)))
        result.append("player_finish_parser_m3u8 -> player_post_first_ts_slice: " + str(list_during(player_finish_parser_m3u8,player_post_first_ts_slice,progress)))
        result.append("player_post_first_ts_slice -> init_video/audio: " + str(list_during(player_post_first_ts_slice,"|".join([init_video,init_audio]),progress)))
        result.append("init_video/audio -> init_audio/video_end: " + str(list_during("|".join([init_video,init_audio]),"|".join([init_audio_end,init_video_end]),progress)))
        result.append("init_audio/video_end -> player_prepared: " + str(list_during("|".join([init_audio_end,init_video_end]),player_prepared,progress)))
        result.append("player_prepared -> player_start: " + str(list_during(player_prepared,player_start,progress)))
        result.append("player_start -> first_frame: " + str(list_during(player_start,first_frame,progress)))
        """
        for i in progress:
            #if re.compile(utp_handle_mirrors).match(i):
                #result.append("utp_handle_mirrors: " + str((3, re.search('\[xml_content_parser\]\ handle_mirrors http://[\d\.]+', i).group())))
            if re.compile(utp_finish_download_first_slice).match(i):
                result.append("utp_finish_download_first_slice_data: " + str((re.search('\[downloader\] on_http_complete \(\(\d+,\d+\),\d+\) \(\d+,\d+,\d+\)', i).group()))
        if "utp_finish_download_first_slice_data:" not in result:
            result.append("utp_finish_download_first_slice_data: " + 'error')
        """


        for i in result: print i

        return result

    def vodHttpPlayProgress(self):
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
                print flag, str(self.calculatorbak(r[0][:18],r[1][:18]))
                return str(self.calculatorbak(r[0][:18],r[1][:18]))+"ms"
            print flag, 'error'
            return 'error'

        #
#user_press = r'.*LETVPlay:\ jumpToPlay\s*$'
        user_press = r'.*injectKeyEvent:\ KeyEvent\ \{\ action=ACTION_DOWN,\ keyCode=KEYCODE_DPAD_CENTER.*'
        user_press = r'.*LETVPlay.*jumpToPlay\s*$'
        tvban_get_url = r'.*LinkShellUtil:\ getURLFromLink\ outPut:(.*$)'
        player_get_url = r'.*MediaPlayerService.*:\ \[(\d+)\]\ setDataSource\((\S+)\)'
        player_request_download = r'.*HTTPStreamCurl:\ \[HTTPStreamCurl\]\ HTTPStreamCurl Connecting to :.*'
        utp_get_first_request = r'.*\[utp_play_handler\] handle_request 127\.0\.0\.1:\d+ bytes=0- /play\?.*'
        utp_request_download_url = r'.*\[downloader\]\ start_download\ http_range:bytes=-\ http://g3\.letv\.cn/vod.*'
        utp_download_first_data = r'.*\[downloader\]\ start_download\ http_range:bytes=-\ .*'
        utp_start_download_first_slice = r'.*\[downloader\]\ start_download\ http_range:bytes=0-\d+ (.*)'
        utp_finish_download_first_slice = r'.*\[downloader\]\ on_http_complete.*'
        #player_request_success = r'.*StreamContentSource::connect OK !!'
        init_video = r'.*Creating\ Video\ Decoder\ video/avc'
        init_video_end = r'.*Video\ Decoder\ instantiante\ end'
        init_audio = r'.*Creating\ Audio\ Decoder\ audio.*'
        init_audio_end = r'.*Audio\ Decoder\ instantiante\ end'
        player_prepared =r'.*MediaPlayerService.*:\ \[(\d+)\]\ notify\ \(\w+,\ 1,\ 0,\ 0\)'
        player_start = r'.*MediaPlayerService.*:\ \[(\d+)\]\ start\s*$'
        first_frame = r'.*MediaPlayerService.*:\ \[(\d+)\]\ notify\ \(\w+,\ 200,\ 3,\ 0\)'

        #after user_press
        regex = [user_press,tvban_get_url,player_get_url,player_request_download,init_video,init_video_end,init_audio,init_audio_end,player_prepared,player_start,first_frame]
        #after utp_get_first_request
        #utp_finish_download_first_slice url must match utp_start_download_first_slice
        regex_first = [utp_get_first_request,utp_request_download_url,utp_download_first_data, utp_start_download_first_slice]

        rr = "|".join(regex)

        progress = []
        logcontents = self.openFile()
        if logcontents == []:
            print 'logcat is null'
            return []

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
        progress.sort()
        print "progress:",len(progress)
        #for i in progress: print i
        result = []

        # init V/A
        av = []
        for i in progress:
            if re.compile("|".join([init_video,init_video_end,init_audio,init_audio_end])).match(i):
                av.append(i)
        av.sort()

        progress.remove(av[1])
        progress.remove(av[2])
        # end init V/A
        for i in progress: print i

        result.append("user_press -> first_frame: " + str(list_during(user_press,first_frame,progress)))
        result.append("user_press -> tvban_get_url: " + str(list_during(user_press,tvban_get_url,progress)))
        result.append("tvban_get_url -> player_get_url: " + str(list_during(tvban_get_url,player_get_url,progress)))
        result.append("player_request_download -> utp_get_first_request: " + str(list_during(player_request_download,utp_get_first_request,progress)))
        result.append("utp_get_first_request -> utp_request_download_url: " + str(list_during(utp_get_first_request,utp_request_download_url,progress)))
        result.append("utp_request_download_url: -> utp_download_first_data: " + str(list_during(utp_request_download_url, utp_download_first_data,progress)))
        result.append("utp_start_download_first_slice -> utp_finish_download_first_slice: " + str(list_during(utp_start_download_first_slice,utp_finish_download_first_slice,progress)))
        result.append("utp_get_first_request -> init_video/audio: " + str(list_during(utp_get_first_request,"|".join([init_video,init_audio]),progress)))
        result.append("init_video/audio -> init_audio/video_end: " + str(list_during("|".join([init_video,init_audio]),"|".join([init_audio_end,init_video_end]),progress)))
        result.append("init_audio/video_end -> player_prepared: " + str(list_during("|".join([init_audio_end,init_video_end]),player_prepared,progress)))
        result.append("player_prepared -> player_start: " + str(list_during(player_prepared,player_start,progress)))
        result.append("player_start -> first_frame: " + str(list_during(player_start,first_frame, progress)))

        for i in result: print i

        return result

    def vodHlsPlayProgress(self):
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
        key_down = r'.*injectKeyEvent:\ KeyEvent\ \{\ action=ACTION_DOWN,\ keyCode=KEYCODE_DPAD_CENTER.*'
        user_press = r'.*LETVPlay.*jumpToPlay\s*$'
        tvban_get_url = r'.*LinkShellUtil:\ getURLFromLink\ outPut:(.*$)'
        player_get_url = r'.*MediaPlayerService.*:\ \[(\d+)\]\ setDataSource\((\S+)\)'
        player_post_m3u8 = r'.*DataSource_M3U8.*:\ \[parseURLs\]\ try\ parseURLs=(\S+)'
        utp_get_first_request = r'.*\[utp_play_handler\]\ handle_request\ 127\.0\.0\.1:\d+\ \ /play?.*'
        utp_request_download_url = r'.*\[downloader\]\ start_download\ http_range:bytes=-\ http://g3\.letv\.cn/vod.*'
        utp_download_first_m3u8 = r'.*\[downloader\]\ start_download\ http_range:bytes=-\ http://.*/.*\.m3u8\?.*'
        utp_start_download_first_slice = r'.*\[downloader\]\ start_download\ http_range:bytes=0-\d+ (.*)'
        utp_finish_download_first_slice = r'.*\[downloader\]\ on_http_complete.*'
        player_finish_parser_m3u8 = r'.*\[init\]\ parseURLs\ Success!\ urlNum\ :\ 3'
        player_post_first_ts_slice = r'.*\[init\]\ \[M3u8\]\ post\ cmd\ for\ start\ first\ url:(\S+)'
        init_video = r'.*Creating\ Video\ Decoder\ video/avc'
        init_video_end = r'.*Video\ Decoder\ instantiante\ end'
        init_audio = r'.*Creating\ Audio\ Decoder\ audio.*'
        init_audio_end = r'.*Audio\ Decoder\ instantiante\ end'
        player_prepared =r'.*MediaPlayerService.*:\ \[(\d+)\]\ notify\ \(\w+,\ 1,\ 0,\ 0\)'
        player_start = r'.*MediaPlayerService.*:\ \[(\d+)\]\ start\s*$'
        first_frame = r'.*MediaPlayerService.*:\ \[(\d+)\]\ notify\ \(\w+,\ 200,\ 3,\ 0\)'


        #after user_press
        regex = [user_press,tvban_get_url,player_get_url,player_post_m3u8,init_video,init_video_end,init_audio,init_audio_end,player_prepared,player_start,first_frame]
        #after utp_get_first_request
        #utp_finish_download_first_slice url must match utp_start_download_first_slice
        regex_first = [utp_get_first_request,utp_request_download_url, utp_download_first_m3u8, utp_start_download_first_slice, player_finish_parser_m3u8, player_post_first_ts_slice]

        rr = "|".join(regex)

        progress = []
        logcontents = self.openFile()
        if logcontents == []:
            print 'logcat is null'
            return []

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
        progress.sort()
        print "progress:",len(progress)
        #for i in progress: print i
        result = []

        # init V/A
        av = []
        for i in progress:
            if re.compile("|".join([init_video,init_video_end,init_audio,init_audio_end])).match(i):
                av.append(i)
        av.sort()

        progress.remove(av[1])
        progress.remove(av[2])
        # end init V/A
        for i in progress: print i

        result.append("user_press -> first_frame: " + str(list_during(user_press,first_frame,progress)))
        result.append("user_press -> tvban_get_url: " + str(list_during(user_press,tvban_get_url,progress)))
        result.append("tvban_get_url -> player_get_url: " + str(list_during(tvban_get_url,player_get_url,progress)))
        result.append("player_get_url -> player_post_m3u8: " + str(list_during(player_get_url,player_post_m3u8,progress)))
#result.append("player_get_url -> player_prepare: " + str(list_during(player_get_url,player_prepare,progress)))
#result.append("player_prepare -> player_post_m3u8: " + str(list_during(player_prepare,player_post_m3u8,progress)))
        result.append("player_post_m3u8 -> utp_get_first_request: " + str(list_during(player_post_m3u8,utp_get_first_request,progress)))
        result.append("utp_get_first_request -> utp_request_download_url: " + str(list_during(utp_get_first_request,utp_request_download_url,progress)))
        result.append("utp_request_download_url -> utp_download_first_m3u8: " + str(list_during(utp_request_download_url,utp_download_first_m3u8,progress)))
        result.append("utp_download_first_m3u8 -> utp_start_download_first_slice: " + str(list_during(utp_download_first_m3u8,utp_start_download_first_slice,progress)))
        result.append("utp_start_download_first_slice -> utp_finish_download_first_slice: " + str(list_during(utp_start_download_first_slice,utp_finish_download_first_slice,progress)))
        result.append("player_post_m3u8 -> player_finish_parser_m3u8: " + str(list_during(player_post_m3u8,player_finish_parser_m3u8,progress)))
        result.append("player_finish_parser_m3u8 -> player_post_first_ts_slice: " + str(list_during(player_finish_parser_m3u8,player_post_first_ts_slice,progress)))
        result.append("player_post_first_ts_slice -> init_video/audio: " + str(list_during(player_post_first_ts_slice,"|".join([init_video,init_audio]),progress)))
        result.append("init_video/audio -> init_audio/video_end: " + str(list_during("|".join([init_video,init_audio]),"|".join([init_audio_end,init_video_end]),progress)))
        result.append("init_audio/video_end -> player_prepared: " + str(list_during("|".join([init_audio_end,init_video_end]),player_prepared,progress)))
        result.append("player_prepared -> player_start: " + str(list_during(player_prepared,player_start,progress)))
        result.append("player_start -> first_frame: " + str(list_during(player_start,first_frame,progress)))

        for i in result: print i

        return result


    def playerProgress(self):
        """return a list includes switch time and each progress time """
        user_press = r'.*Launcher.*:\ T2LauncherActivity\ --\ onKeyDown:\ KeyEvent\ \{\ action=ACTION_DOWN,\ keyCode=KEYCODE_0.*'
        launcher_get_url = r'.*Launcher.*:\ LivePlayerController\ --\ play\(\)\ -\ uri:(\S+)\ pip:\ false\s*$'
        player_get_url = r'.*MediaPlayerService.*:\ \[(\d+)\]\ setDataSource\((\S+)\)'
        player_get_app_init_time = r'.*MediaPlayerService.*:\s+request-time\ :\ (\d+)\s*$'
        player_prepare = r'.*MediaPlayerService.*:\ \[(\d+)\]\ prepareAsync\s*$'
        post_m3u8 = r'.*DataSource_M3U8.*:\ \[M3U8\]\ try\ parseURLs=(\S+)'
        get_first_m3u8 = r'.*DataSource_M3U8.*:\s+mHttpResponseCode\ =\ 200\s*$'
        post_first_ts_slice = r'.*DataSource_M3U8.*:\ \[M3U8\]----->post\ cmd\ for\ start\ first\ url:(\S+),\ knowedFileSize:0'
        player_prepared =r'.*MediaPlayerService.*:\ \[(\d+)\]\ notify\ \(\w+,\ 1,\ 0,\ 0\)'
        player_start = r'.*MediaPlayerService.*:\ \[(\d+)\]\ start\s*$'
        player_start_done = r'.*MediaPlayerService.*:\ \[(\d+)\]\ start\ done\s*$'
        first_frame = r'.*MediaPlayerService.*:\ \[(\d+)\]\ notify\ \(\w+,\ 200,\ 3,\ 0\)'
        start_loading = r'.*MediaPlayerService.*:\ \[(\d+)\]\ notify\ \(\w+,\ 200,\ 701,\ 0\)\s*$'
        end_loading = r'.*MediaPlayerService.*:\ \[(\d+)\]\ notify\ \(\w+,\ 200,\ 702,\ 0\)\s*$'
        player_stop = r'.*MediaPlayerService.*:\ \[(\d+)\]\ stop\s*$'
        player_stop_done = r'.*MediaPlayerService.*:\ \[(\d+)\]\ stop\ done\s*$'
        player_release = r'.*MediaPlayerService.*: disconnect\((\d+)\)\ from\ pid\ \d+\s*$'
        player_release_done    = r'.*MediaPlayerService.*:\ \[(\d+)\]\ disconnect\ done\s*$'

        regex = [user_press,launcher_get_url,player_get_url, player_get_app_init_time, player_prepare, post_m3u8,get_first_m3u8, post_first_ts_slice,\
         player_prepared, player_start,player_start_done, first_frame, start_loading, end_loading, player_stop,player_stop_done,  player_release, player_release_done]
        rr = "|".join(regex)

        progress = []
        logcontents = self.openFile()
        index = 0
        last = 0
        if logcontents != []:
            for line in logcontents:
                if re.compile(user_press).match(line):
                    index = logcontents.index(line)
                    last = index
                    break
            for line in logcontents[index:]:
                if re.compile(first_frame).match(line):
                    last = logcontents.index(line)+1
                    break
        else:
            return
        for line in logcontents[index:last]:
            if re.compile(rr).match(line):
                progress.append(line)

        during = []
        result = []
        for line in progress:
            #print line
            if re.compile("|".join([user_press, first_frame])).match(line):
                during.append(line)
        if len(during)%2 !=0 or len(during)==0:
            print "not start in the end"
        else:
            i=0
            while i < len(during):
                countTime = self.calculatorbak(during[i][:18], during[i+1][:18])
                result.append("Time:"+str(countTime))
                onep = progress[progress.index(during[i]):progress.index(during[i+1])+1]
                onesp = []
                if len(onep) != len(regex):
                    for rep in regex:
                        for each in onep:
                            if re.compile(rep).match(each):
                                onesp.append(each)
                                break
                    onesp.sort()
                else:
                    onesp = onep
                #print exceed time line
                if countTime > 2000:
                    for ll in onesp: print ll
                #while the output log grogress is right
                if len(onesp) == len(regex):
                    j=0
                    while j < len(onesp)-1:
                        result.append(self.calculatorbak(onesp[j][:18], onesp[j+1][:18]))
                        j += 1
                    #while the output log is more then range
                else:
                    result.append("ERROR")
                    print "ERROR"

                i += 2
        return result

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


    def calculator(self, start_str, end_str):
        """
        params: time format like 12-19 17:31:34.166
        return: int mseconds
        """
        year = datetime.datetime.today().year

        start = start_str.split('.')
        end = end_str.split('.')

        start[0] = str(year) + '-' + start[0]
        end [0] = str(year) + '-' + end[0]
        toTime_start = time.mktime(time.strptime(start[0], '%Y-%m-%d %H:%M:%S'))
        toTime_end = time.mktime(time.strptime(end[0], '%Y-%m-%d %H:%M:%S'))
        s = int(toTime_end - toTime_start)
        if int(end[1]) < int(start[1]):
            s -= 1
            end[1] = '1' + end[1]
        ms = int(end[1])*0.001 - int(start[1])*0.001
        return int(s*1000+ms*1000)

    def playerPrepareTime(self):
        """ param: log file directory
            func: if player prepare ok then return ms for player prepare time else return -1
            """
        get_list_start = ''
        get_list_end = ''
        pattern_start = re.compile(r'.*MediaPlayerService.*Client\((\d+)\)\ constructor')
        all_lines = self.openFile()

        pipeline = 1
        for line in all_lines:
            match_start = pattern_start.match(line)
            if match_start:
                pipeline = match_start.group(1)
                get_list_start = match_start.group()
            #pattern_end = re.compile(r'.*MediaPlayerService.*:\ \[%s\] notify\ \(\w+,\ 1,\ 0,\ 0\)' % pipeline)
            pattern_end = re.compile(r'.*MediaPlayerService.*:\ \[%s\] start\ done' % pipeline)

            match_end = pattern_end.match(line)
            if match_end:
                get_list_end = match_end.group()
        print get_list_start
        print get_list_end

        if get_list_start == '' or get_list_end == '':
            self.error = 'cannot play after 30s'
            return -1

        """_start_time = get_list_start.split()[1][6:]
        _end_time = get_list_end.split()[1][6:]
        start_time = _start_time.split('.')
        end_time = _end_time.split('.')
        during = (int(end_time[0]) * 1000 + int(end_time[1])) - (int(start_time[0]) * 1000 + int(start_time[1]))"""
        during = self.calculator(get_list_start[:18], get_list_end[:18])
        print during
        return str(during)

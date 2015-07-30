performacelist = ["com.phone.smoke.LeJian#testLeJianPerformance", "com.phone.smoke.LiveVideo#testLivePlayPerformance","com.phone.smoke.LeJian#testMediaHandongM3u8","com.phone.smoke.LeJian#testDtsHlsM3u8","com.phone.smoke.LeJian#testLongTsM3u8", "com.phone.smoke.LeJian#testHttpH264DolbyM3u8"]
if test.names[len(test.names)-1] in performacelist and test.result=="PASS" :
    try:
        import cloudLogAnalyse
        c = cloudLogAnalyse.cloudStatus(os.path.join(test.resultDirectory,test.logDirectory, "logcat_main.txt"))
        with open(os.path.join(test.resultDirectory,test.logDirectory, "display.txt"), "a+") as fp:
            for line in c.vodHlsPlayProgress(run_sh_command('adb -s %s shell getprop ro.build.product' %option.serialno).strip()):
                fp.write(line+"\r\n")
    except Exception, e:
        print e
livelist = ['com.letv.cloudvideo.TvBanTestCase#testLiveChangeChannel1To2', 'com.letv.cloudvideo.TvBanTestCase#testLiveChangeChannel2To3', 'com.letv.cloudvideo.TvBanTestCase#testLiveChangeChannel3To4', 'com.letv.cloudvideo.TvBanTestCase#testLiveChangeChannel4To5', 'com.letv.cloudvideo.TvBanTestCase#testLiveChangeChannel5To6']
if test.names[len(test.names)-1] in livelist:
    try:
        import cloudLogAnalyse_TV
        print "logcat dir: "+os.path.join(test.resultDirectory,test.logDirectory, "logcat_main.txt")
        tv = cloudLogAnalyse_TV.cloudStatus(os.path.join(test.resultDirectory,test.logDirectory, "logcat_main.txt"))
        with open(os.path.join(test.resultDirectory,test.logDirectory, "display.txt"), "a+") as fp:
            for line in tv.livePlayProgress():
                fp.write(line+"\r\n")
    except Exception, e:
        print e

vodlist = ['com.letv.cloudvideo.TvBanTestCase#testPlayVodfirst_ts_long','com.letv.cloudvideo.TvBanTestCase#testPlayVoda']
if test.names[len(test.names)-1] in vodlist:
    try:
        import cloudLogAnalyse_TV
        tv = cloudLogAnalyse_TV.cloudStatus(os.path.join(test.resultDirectory,test.logDirectory, "logcat_main.txt"))
        with open(os.path.join(test.resultDirectory,test.logDirectory, "display.txt"), "a+") as fp:
            fp.write(tv.playerPrepareTime()+"\r\n")
    except Exception, e:
        print e

if test.names[len(test.names)-1] in "com.letv.cloudvideo.TvBanTestCase#testPlay1080P":
    try:
        import cloudLogAnalyse_TV
        tv = cloudLogAnalyse_TV.cloudStatus(os.path.join(test.resultDirectory,test.logDirectory, "logcat_main.txt"))
        with open(os.path.join(test.resultDirectory,test.logDirectory, "display.txt"), "a+") as fp:
            for line in tv.vodHlsPlayProgress():
                fp.write(line+"\r\n")
    except Exception, e:
        print e


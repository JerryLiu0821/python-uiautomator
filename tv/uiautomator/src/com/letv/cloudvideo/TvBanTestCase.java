package com.letv.cloudvideo;

import com.android.uiautomator.core.UiObject;
import com.android.uiautomator.core.UiObjectNotFoundException;

public class TvBanTestCase extends BaseCase {

    public final String TAG = "TVBAN";

    public void testPlay1080P() throws UiObjectNotFoundException{
        runShell("am start -a android.intent.action.MAIN -n com.letv.tv/.activity.MainActivity");
        sleepInt(5);
        UiObject loginPage = UiObjectText("暂不登录"); 
        if(loginPage.exists()){
            loginPage.clickAndWaitForNewWindow();
            sleepInt(1);
        }
        UiObject channel = UiObjectText("频道");
        if (!channel.exists()){
            fail("cannot open tvban");
        }
        addInfo(TAG, "goto 频道");
        press_Down(4, 1);
        press_Left(5, 1);
        press_Right(2, 1);
        addInfo(TAG, "click 1080p");
        UiObject p1080 = UiObjectText("1080P");
        p1080.click();
        sleepInt(1);
        p1080.clickAndWaitForNewWindow();
        sleepInt(5);
        addInfo(TAG, "goto video list page");
        press_Down(1, 1);
        addInfo(TAG, "goto deatil page");
        press_Center(1, 5);
        UiObject play = UiObjectText("播放");
        if(!play.exists()){
            addInfo(TAG, "detail page not display, wait for 10 seconds");
            sleepInt(10);
        }
        play.click();
        sleepInt(15);
        exitTvBan();

    }

    public void exitTvBan() throws UiObjectNotFoundException{
        UiObject exit = UiObjectText("退出");
        for(int i=0; i<10;i++){
            press_Back(1, 1);
            if(exit.exists()){
                exit.click();
                break;
            }
        }
    }

    public void testLiveChangeChannel1To2(){
        changeChannel(8);
    }

    public void testLiveChangeChannel2To3(){
        changeChannel(9);
    }

    public void testLiveChangeChannel3To4(){
        changeChannel(10);
    }

    public void testLiveChangeChanne41To5(){
        changeChannel(11);
    }

    public void testLiveChangeChannel5To6(){
        changeChannel(12);
    }

    public void changeChannel(int num){
        runShell("input keyevent 4402");
        sleepInt(5);
        press_Back(1, 1);
        press_Right(1, 5);
        runShell("input keyevent "+String.valueOf(num));
        sleepInt(85);
        runShell("input keyevent 166");
        sleepInt(30);
    }


    public void testPlayVodfirst_ts_long(){
        startVideo("http://10.154.250.32:8080/vod/first_ts_long.m3u8");
        press_Back(2, 1);
    }

    public void testPlayVoda(){
        startVideo("http://10.154.250.32:8080/vod/a.m3u8");
        press_Back(2, 1);
    }

    public void startVideo(String url){
        runShell("am start -a android.intent.action.MAIN -c android.intent.category.LAUNCHER -f 0x10200000 -n com.stv.filemanager/.FileExplorerTabActivity");
        sleepInt(5);
        String cmd = "am start -a android.intent.action.VIEW -d "+url+" -n com.stv.videoplayer/.MainActivity";
        addInfo(TAG, cmd);
        addInfo(TAG, url);
        runShell(cmd);
        sleepInt(30);
    }

}

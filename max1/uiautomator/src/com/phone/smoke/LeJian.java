package com.phone.smoke;

import com.android.uiautomator.core.UiObject;
import com.android.uiautomator.core.UiObjectNotFoundException;
import com.android.uiautomator.core.UiSelector;

public class LeJian extends BaseCase {

    public final static String TAG = "LeJian";

    public void tearDown() throws Exception {
        super.tearDown();
        press_Back(2, 1);
    }

    public void testLeJianPerformance() throws UiObjectNotFoundException {
        press_Home(2, 1);
        swipeToRight();
        sleepInt(2);
        UiObject start = UiObjectRid("com.android.launcher3:id/sarrs_click_to_start");
        if (start.exists()) {
            start.click();
            sleepInt(10);
        }
        addInfo(TAG, "select first item to play");
        UiObject LeJianList = UiObjectRid("com.android.launcher3:id/sarrs_ptr_recyclerview");
        UiObject first = LeJianList.getChild(new UiSelector().index(0));
        first.clickAndWaitForNewWindow();
        sleepInt(2);
        UiObject video_container = UiObjectRid("com.letv.android.client:id/main_player_video_view_container");
        sleepInt(5);
        video_container.click();
        sleepInt(5);
        checkStatus();
        press_Back(1, 2);
    }

    public void testMediaHandongM3u8(){
        runVod("http://10.154.250.32:8081/media/handong/desc.m3u8");
    }
    public void testDtsHlsM3u8(){
        runVod("http://10.154.250.32:8081/DTS/HLS/a.m3u8");
    }
    public void testLongTsM3u8(){
        runVod("http://10.154.250.32:8081/share/test_for_long_ts/download/desc.m3u8");
    }

    public void testHttpH264DolbyM3u8(){
        runVod("http://10.154.250.32:8081/http_live/h264_dolby/movie1/a.m3u8");
    }

    public void runVod(String url){
        runShell("am start -d "+url+" -n com.android.videoplayer/.PlayerActivity");
        sleepInt(10);
    }

    public void checkStatus() throws UiObjectNotFoundException {
        UiObject loading = UiObjectRid("com.letv.android.client:id/player_loading_progress_bar");
        UiObject retry = UiObjectRid("com.letv.android.client:id/player_tips_function_btn");
        for (int i = 0; i < 5; i++) {
            if (loading.exists()) {
                addInfo(TAG, "loading");
                sleepInt(5);
            } else {
                addInfo(TAG, "finish loading");
                break;
            }
        }
        if (retry.exists()) {
            addInfo(TAG, "retry happened, retry one time");
            retry.click();
            sleepInt(10);
            if (retry.exists()) {
                failed("retry to play");
            }
        }

    }
}

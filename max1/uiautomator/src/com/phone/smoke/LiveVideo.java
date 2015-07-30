package com.phone.smoke;

import java.util.Random;
import android.os.Bundle;

import com.android.uiautomator.core.UiObject;
import com.android.uiautomator.core.UiObjectNotFoundException;
import com.android.uiautomator.core.UiSelector;

public class LiveVideo extends BaseCase {

    public final static String TAG = "LiveVideo";
    public UiObject retry;
    UiObject live = UiObjectRid("com.android.launcher3:id/live_circle");
    UiObject liveTV = UiObjectText("卫视");
    UiObject liveContent = new UiObject(new UiSelector().className("android.widget.FrameLayout").index(1));

    public void setUp() throws Exception {
        super.setUp();
        press_Home(2, 1);
    }
    public void tearDown() throws Exception {
        super.tearDown();
        press_Back(6, 1);
    }

    public void enterLive() throws UiObjectNotFoundException {
        live.click();
        sleepInt(5);
        UiObject upgradeRid = UiObjectRid("com.letv.android.letvlive:id/next_time");
        if(upgradeRid.exists()){
            addInfo(TAG, "do not upgrade");
            upgradeRid.click();
            sleepInt(1);
        }
        UiObject pkg = UiObjectPackage("com.letv.android.letvlive");
        if(!pkg.exists()){
            failed("enter live failed");
        }
    }

    public void testChangeChannel() throws UiObjectNotFoundException {
        //UiObject live = UiObjectRid("com.android.launcher3:id/live_circle");
        //live.click();
        /*
        sleep(5000);
        UiObject liveTV = UiObjectText("直播");
        liveTV.click();
        sleep(5000);
        UiObject liveContent = new UiObject(new UiSelector().className("android.widget.FrameLayout").index(1));
        liveContent.click();
        sleep(3000);
        */
        enterLive();
        liveTV.click();
        sleepInt(5);
        liveContent.click();
        sleepInt(3);
        for (int i = 0; i < times; i++) {
            addInfo(TAG,"change channel");
            device.swipe(1440, 340, 0, 340, 30);
            sleepInt(10);
            checkStatus();
        }
    }

    public void testLiveInterHome() throws UiObjectNotFoundException {
        enterLive();
        liveTV.click();
        sleepInt(5);
        liveContent.click();
        sleepInt(3);
        for (int i = 0; i < times; i++) {
            addInfo(TAG,"switch");
            press_Home(1,3);
            // live.click();
            UiObject scontainer = UiObjectRid("com.android.systemui:id/acsv");
            UiObject container = scontainer.getChild(new UiSelector().index(0));
            addInfo(TAG, "press 1 index in setting csv");
            press_Menu(1, 2);
            container.getChild(new UiSelector().index(1)).click();
            sleepInt(10);
            checkStatus();
        }
    }

    public void testLiveUnlock() throws UiObjectNotFoundException {
        enterLive();
        liveTV.click();
        sleepInt(5);
        liveContent.click();
        sleepInt(3);
        try {
            for (int i = 0; i < times; i++) {
                addInfo(TAG,"sleep");
                device.sleep();
                sleepInt(3);
                device.wakeUp();
                sleepInt(2);
                swipeToTop();
                sleepInt(10);
                checkStatus();
            }
        } catch (Exception e) {
            e.printStackTrace();
        }

    }
    public void testLivePlayPerformance() throws UiObjectNotFoundException {
        enterLive();
        addInfo(TAG, "click first live item to play");
        device.click(650, 350);
        sleepInt(10);

    }

    public void checkStatus(){
        UiObject liveVideo = UiObjectRid("com.letv.android.letvlive:id/main_player_lower_container");
        if (!liveVideo.exists()) {
            failed("switch to Live failed");
        }
        UiObject loading = UiObjectRid("com.letv.android.client:id/player_loading_progress_bar");
        for (int i = 0; i < 5; i++) {
            if (loading.exists()) {
                addInfo(TAG, "loading");
                sleepInt(5);
            } else {
                addInfo(TAG, "finish loading");
                break;
            }
        }

    }
}

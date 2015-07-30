package com.phone.smoke;

import java.util.Random;
import android.os.Bundle;

import com.android.uiautomator.core.UiObject;
import com.android.uiautomator.core.UiObjectNotFoundException;
import com.android.uiautomator.core.UiSelector;

public class LetvVideo extends BaseCase {

    public final static String TAG = "LetvVideo";
    public UiObject retry;
    UiObject vod = UiObjectRid("com.letv.android.client:id/main_player_video_view_container");

    public void tearDown() throws Exception {
        super.tearDown();
        press_Back(6, 1);
    }

    public void gotoLetvVideo(String which) throws UiObjectNotFoundException {
        press_Home(2, 1);
        UiObjectText("乐视视频").clickAndWaitForNewWindow();
        sleepInt(3);
        UiObject upgrade_later = UiObjectRid("com.letv.android.client:id/update_later_btn");
        if (upgrade_later.exists()) {
            upgrade_later.click();
            sleepInt(2);
        }

        String channelList[] = new String[] { "电视剧", "电影", "综艺", "动漫", "3D频道",
                "4K频道", "2K频道", "音乐", "体育" };

        UiObject my = UiObjectText("我的");
        UiObject index = UiObjectText("首页");
        UiObject channel = UiObjectText("频道");
        UiObject live = UiObjectText("直播");
        UiObject discovery = UiObjectText("发现");

        gotoChannel("频道");
        if (which == "") {
            which = channelList[Math.abs(new Random().nextInt())
                    % channelList.length];
        }
        gotoChannel(which);
        sleepInt(3);
        device.click(487, 1313);
        sleepInt(10);
        UiObject title = UiObjectRid("com.letv.android.client:id/tips_top_title");
        retry = UiObjectRid("com.letv.android.client:id/player_tips_function_btn");
        if (retry.exists()) {
            addInfo(TAG, retry.getText());
            retry.click();
            sleepInt(10);
            if (retry.exists()) {
                failed("play " + title.getText() + " failed: " + retry.getText());
            }
        }

    }

    public void testPlayNext() throws UiObjectNotFoundException {
    	gotoLetvVideo("电视剧");
    	sleepInt(1);
    	screenShot("beforeSeek");
    	for (int i = 1; i < 15; i++) {
    		if (!device.swipe(0, 340, 1440, 340, 200))
    			failed("failed to jump to next");
    	    addInfo(TAG,"seek "+String.valueOf(i));
    		sleepInt(1);
    		if (!vod.exists()) {
    			failed("video failed to play");
    		}
    	}
    	screenShot("afterSeek");
    }

    /*
     * 快进快退
     */
    public void testXunhuan() throws UiObjectNotFoundException {
        for (int i = 0; i < times; i++) {
            addInfo(TAG, "快进");
            swipeToRight();
            sleepInt(10);
            addInfo(TAG, "快退");
            swipeToLeft();
            sleepInt(10);
        }
    }

    /*
     * 播放视频过程中切换音量
     */
    public void testChangeVolume() throws UiObjectNotFoundException {
        gotoLetvVideo("");
        device.click(592, 524);
        sleep(500);
        addInfo(TAG, "switch to orientation");
        device.click(1400, 854);
        sleepInt(8);
        for (int i = 0; i < times; i++) {
            addInfo(TAG, "volume up");
            device.swipe(2074, 1191, 2074, 491, 20);
            sleepInt(8);
            addInfo(TAG, "volume down");
            device.swipe(2074, 491, 2074, 1191, 20);
            sleepInt(8);
        }
    }

    /*
     * 在连续剧中选集播放
     */
    public void testSelectItemPlay() throws UiObjectNotFoundException {
        gotoLetvVideo("电视剧");
        UiObject items = UiObjectRid("com.letv.android.client:id/detailplay_half_video_expandable_gridview");
        for (int i = 0; i < times; i++) {
            int which = Math.abs(new Random().nextInt())
                    % items.getChildCount();
            addInfo(TAG, "select " + which + 1);
            items.getChild(new UiSelector().index(which)).click();
            sleepInt(10);
            checkStatus();

        }
    }

    /*
     * 播放过程中暂停
     */
    public void testPausePlay() throws UiObjectNotFoundException {
        gotoLetvVideo("");
        device.click(592, 524);
        sleep(500);
        addInfo(TAG, "switch to orientation");
        device.click(1400, 854);
        sleepInt(8);
        for (int i = 0; i < times; i++) {
            addInfo(TAG, "暂停");
            device.click(800, 600);
            sleepInt(1);
            device.click(64, 1417);
            sleepInt(10);
            addInfo(TAG, "播放");
            device.click(800, 600);
            sleepInt(1);
            device.click(64, 1417);
            sleepInt(10);
        }

    }
    /*
     * 快进
     */
    public void testSeek() throws UiObjectNotFoundException {
        gotoLetvVideo("电影");
        device.click(592, 524);
        sleep(500);
        addInfo(TAG, "switch to orientation");
        device.click(1400, 854);
        sleepInt(8);
        for (int i = 0; i < times; i++) {
            swipeToRight();
            sleepInt(8);
            checkStatus();
            swipeToLeft();
            sleepInt(8);
        }

    }

    /*
     * 大小屏切换
     */
    public void testSwitchOriention() throws UiObjectNotFoundException {
        gotoLetvVideo("");
        for (int i = 0; i < times; i++) {
            addInfo(TAG, "switch to orientation");
            device.click(592, 524);
            sleep(500);
            device.click(1400, 854);
            sleepInt(8);

            addInfo(TAG, "back to small screen");
            device.click(2000, 900);
            sleepInt(1);
            device.click(2479, 1380);
            sleepInt(8);
        }
    }

    /*
     * 不同分辨率下切换大小屏
     */
    public void testSwitchOrientationWithResolution()
            throws UiObjectNotFoundException {
        gotoLetvVideo("");
        for (int i = 0; i < times; i++) {
            String reso[] = new String[] { "急速", "流畅", "标清", "高清", "超清" };
            for (int j = 0; j < reso.length; j++) {
                device.click(592, 524);
                sleep(500);
                addInfo(TAG, "switch to orientation");
                device.click(1400, 854);
                sleepInt(8);
                gotoResolution(reso[j]);
                // back to small screen
                device.click(2000, 900);
                sleepInt(1);
                device.click(2484, 1385);
                sleepInt(8);
            }
        }

    }

    /*
     * 切换分辨率
     */
    public void testSwitchResolution() throws UiObjectNotFoundException {
        gotoLetvVideo("电影");
        device.click(592, 524);
        sleep(500);
        addInfo(TAG, "switch to orientation");
        device.click(1400, 854);
        sleepInt(8);
        for (int i = 0; i < times; i++) {
            switchResolution();
        }

    }
    /*
     * 播放3分钟视频观察loading情况
     */
    public void testPlay3minCheckLoading() throws UiObjectNotFoundException {
        gotoLetvVideo("");
        device.click(592, 524);
        sleep(500);
        addInfo(TAG, "switch to orientation");
        device.click(1400, 854);
        sleepInt(180);
    }

    public void switchResolution() throws UiObjectNotFoundException {
        String resolution[] = new String[] { "急速", "超清", "流畅", "超清", "标清",
                "超清", "高清", "超清" };
        for (int i = 0; i < resolution.length; i++) {
            gotoResolution(resolution[i]);
        }
    }

    public void promptResolutionMenu() {
        device.click(2000, 100);
        sleepInt(2);
        device.click(2330, 1367);
        sleepInt(1);
    }

    public void gotoResolution(String text) {
        addInfo(TAG, text);
        if (text.equals("超清")) {
            promptResolutionMenu();
            device.click(2310, 916);
            sleepInt(10);
        } else if (text.equals("标清")) {
            promptResolutionMenu();
            device.click(2310, 1064);
            sleepInt(10);
        } else if (text.equals("流畅")) {
            promptResolutionMenu();
            device.click(2310, 1164);
            sleepInt(10);
        } else if (text.equals("急速")) {
            promptResolutionMenu();
            device.click(2310, 1258);
            sleepInt(10);
        } else if (text.equals("高清")) {
            promptResolutionMenu();
            device.click(2310, 995);
            sleepInt(10);
        } else {

        }
        checkStatus();
    }

    public void gotoChannel(String text) throws UiObjectNotFoundException {
        UiObject channel = UiObjectText(text);
        addInfo(TAG, "goto " + text);
        channel.click();
        sleepInt(1);
    }

    public void checkStatus() {
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
        if (retry.exists()) {
            failed("retry to play");
        }

    }

}

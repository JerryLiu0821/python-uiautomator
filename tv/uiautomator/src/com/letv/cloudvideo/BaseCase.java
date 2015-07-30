/*
 * 
 * BaseCase for TV
 * 
 */

package com.letv.cloudvideo;

import java.io.ByteArrayOutputStream;
import java.io.File;
import java.io.IOException;
import java.io.InputStream;

import android.app.Activity;
import android.os.Bundle;

import com.android.uiautomator.core.UiDevice;
import com.android.uiautomator.core.UiObject;
import com.android.uiautomator.core.UiObjectNotFoundException;
import com.android.uiautomator.core.UiSelector;
import com.android.uiautomator.core.UiWatcher;
import com.android.uiautomator.testrunner.UiAutomatorTestCase;

public abstract class BaseCase extends UiAutomatorTestCase {

    // define keycode
    public static final int KEYCODE_HOME = 3;
    public static final int KEYCODE_BACK = 4;
    public static final int KEYCODE_UP = 19;
    public static final int KEYCODE_DOWN = 20;
    public static final int KEYCODE_LEFT = 21;
    public static final int KEYCODE_RIGHT = 22;
    public static final int KEYCODE_CENTER = 23;
    public static final int KEYCODE_VOLUME_UP = 24;
    public static final int KEYCODE_VOLUME_DOWN = 25;
    public static final int KEYCODE_MENU = 187;
    public static final int KEYCODE_VOLUME_MUTE = 164;
    public static final int KEYCODE_CHANNEL_UP = 166;
    public static final int KEYCODE_CHANNEL_DOWN = 167;
    public static final int KEYCODE_SETTING = 176;
    public static final String TAG = "BaseCase";

    public static final String path = "/data/local/tmp/hometest/";
    public static UiDevice device;
    public int runTimes = 1;

    private Process pLogcat;

    @Override
    protected void setUp() throws Exception {
        super.setUp();
        addInfo(TAG, "setup");
        File f = new File(path);
        if (!f.exists() || !f.isDirectory()) {
            f.mkdir();
        }
        Bundle count = getParams();
        if (count.getString("count") != null) {
            runTimes = Integer.parseInt(count.getString("count"));
        }
        device = getUiDevice();
        device.registerWatcher("ANR", anrWatcher);
        device.registerWatcher("FC", fcWatcher);
    }

    @Override
    protected void tearDown() throws Exception {
        addInfo(TAG, "teardown");
        device.removeWatcher("ANR");
        device.removeWatcher("FC");
        super.tearDown();
    }

    public void sleepInt(int second) {
        sleep(second * 1000);
    }

    public UiObject UiObjectRid(String rid) {
        return new UiObject(new UiSelector().resourceId(rid));
    }

    public UiObject UiObjectText(String text) {
        return new UiObject(new UiSelector().text(text));
    }

    public void screenShot(String filename) {
        File f = new File(path + filename + ".png");
        if (f.exists()) {
            f = new File(path + filename + "_1.png");
        }
        addInfo("screenshot", f.getAbsolutePath());
        getUiDevice().takeScreenshot(f);
    }

    public void screenShot(String path, String filename) {
        if(!path.endsWith("/")){
            path = path + "/";
        }
        File p = new File(path);
        if(!p.isDirectory()){
            p.mkdirs();
        }
        File f = new File(path + filename + ".png");
        if (f.exists()) {
            f = new File(path + filename + "_1.png");
        }
        addInfo("screenshot", f.getAbsolutePath());
        getUiDevice().takeScreenshot(f);
    }

    public String getModel(){
        return runShell("getprop ro.product.model");
    }

    public String getBuild(){
        return runShell("getprop ro.build.description");
    }

    public void addInfo(String key, String value) {
        Bundle b = new Bundle();
        b.putString(key, value);
        getAutomationSupport().sendStatus(Activity.RESULT_OK, b);
    }

    public void press_KeyCode(int times, int keycode, int sleepTime) {
        if (times < 1)
            return;
        for (int i = 1; i <= times; i++) {
            getUiDevice().pressKeyCode(keycode);
            sleepInt(sleepTime);
        }
    }

    public void press_Home(int times, int sleepTime) {
        press_KeyCode(times, KEYCODE_HOME, sleepTime);
    }

    public void press_Back(int times, int sleepTime) {
        press_KeyCode(times, KEYCODE_BACK, sleepTime);
    }

    public void press_Up(int times, int sleepTime) {
        press_KeyCode(times, KEYCODE_UP, sleepTime);
    }

    public void press_Down(int times, int sleepTime) {
        press_KeyCode(times, KEYCODE_DOWN, sleepTime);
    }

    public void press_Left(int times, int sleepTime) {
        press_KeyCode(times, KEYCODE_LEFT, sleepTime);
    }

    public void press_Right(int times, int sleepTime) {
        press_KeyCode(times, KEYCODE_RIGHT, sleepTime);
    }

    public void press_Center(int times, int sleepTime) {
        press_KeyCode(times, KEYCODE_CENTER, sleepTime);
    }

    public void press_Menu(int times, int sleepTime) {
        press_KeyCode(times, KEYCODE_MENU, sleepTime);
    }

    public void press_VolumeUp(int times, int sleepTime) {
        press_KeyCode(times, KEYCODE_VOLUME_UP, sleepTime);
    }

    public void press_VolumeDown(int times, int sleepTime) {
        press_KeyCode(times, KEYCODE_VOLUME_DOWN, sleepTime);
    }

    public void press_ChannelUp(int times, int sleepTime) {
        press_KeyCode(times, KEYCODE_CHANNEL_DOWN, sleepTime);
    }

    public void press_ChannelDown(int times, int sleepTime) {
        press_KeyCode(times, KEYCODE_CHANNEL_DOWN, sleepTime);
    }


    public String runShell(String command) {
        try {
            Process process = Runtime.getRuntime().exec(command);
            int exitValue = process.waitFor();
            if (0 != exitValue) {
                addInfo(TAG, "run shell failed: " + exitValue);
            }
            InputStream in = process.getInputStream();
            ByteArrayOutputStream outStream = new ByteArrayOutputStream();
            byte[] data = new byte[1024];
            int count = -1;
            while ((count = in.read(data, 0, 1024)) != -1)
                outStream.write(data, 0, count);
            data = null;
            return new String(outStream.toByteArray(), "UTF-8");
        } catch (Throwable e) {
            addInfo(TAG, "run shell failed!!");
            e.printStackTrace();
            return null;
        }

    }

    public UiWatcher anrWatcher = new UiWatcher() {

        @Override
        public boolean checkForCondition() {
            UiObject anrWindows = new UiObject(new UiSelector().className(
                    "android.widget.TextView").textContains("要将它关闭吗"));
            String whichApp = "";
            if (anrWindows.exists()) {
                try {
                    UiObject anr = new UiObject(new UiSelector().className(
                            "android.widget.Button").text("确定"));
                    addInfo("anr", "anr happended");
                    whichApp = anr.getText();
                    anr.click();
                    whichApp = whichApp.split("。")[0].split(" ")[0];
                } catch (UiObjectNotFoundException e) {
                    e.printStackTrace();
                } finally {
                    screenShot(whichApp+"_anr");
                    fail("ANR occurred");
                }
                return true;
            } else {
                return false;
            }
        }
    };
    public UiWatcher fcWatcher = new UiWatcher() {

        @Override
        public boolean checkForCondition() {
            UiObject fcWindows = new UiObject(new UiSelector().className(
                    "android.widget.TextView").textContains("已停止运行。"));
            String whichApp = "";
            if (fcWindows.exists()) {
                try {
                    UiObject fc = new UiObject(new UiSelector().className(
                            "android.widget.Button").text("确定"));
                    addInfo("forceclosed", "force closed happened");
                    whichApp = fcWindows.getText();
                    fc.click();
                    whichApp = whichApp.split("。")[0].split("，")[1].split("”")[0].split("“")[1];
                } catch (UiObjectNotFoundException e) {
                    e.printStackTrace();
                } finally {
                    screenShot(whichApp+"_force_closed");
                    fail("Force Closed occurred");
                }
                return true;
            } else {
                return false;
            }
        }
    };

    public void startLogcat(String filename){
        if(pLogcat != null){
            addInfo(TAG, "logcat is running, kill it");
            pLogcat.destroy();
        }
        try {
            pLogcat = Runtime.getRuntime().exec(new String[]{"sh", "-c", "logcat -v time >"+path+filename+" &"});
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    public void stopLogcat(){
        if(pLogcat != null){
            addInfo(TAG, "kill logcat");
            pLogcat.destroy();
        }
    }

    public void UiCollection(){

    }

}

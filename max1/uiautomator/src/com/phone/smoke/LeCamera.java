package com.phone.smoke;

import java.io.File;
import java.util.ArrayList;

import com.android.uiautomator.core.UiObject;
import com.android.uiautomator.core.UiObjectNotFoundException;
import com.android.uiautomator.core.UiWatcher;

public class LeCamera extends BaseCase {

    private final static String TAG = "Camera";

    public void setUp() throws Exception {
        super.setUp();
        press_Home(1, 2);
        addInfo(TAG, "launch camera");
        runShell("am start com.android.camera2/com.android.camera.CameraLauncher");
        device.registerWatcher("saveMode", saveModeWatcher);
        sleepInt(5);
    }

    public void tearDown() throws Exception {
        super.tearDown();
        device.removeWatcher("saveMode");
        press_Back(1, 2);
    }

    /*
     * capture photo
     */
    public void testTakePhoto() throws UiObjectNotFoundException {
        int prenum = checkPhoto();
        UiObject capture = UiObjectRid("com.android.camera2:id/shutter_button");
        UiObject preview = UiObjectRid("com.android.camera2:id/preview_thumb_frame");
        UiObject agree = UiObjectRid("android:id/btn_agree");
        addInfo(TAG, "click capture");
        capture.click();
        sleepInt(5);
        int aftnum = checkPhoto();
        if (prenum == aftnum) {
            failed("capture photo failed");
        }
    }

    /*
     * switch between sensor in camera
     */
    public void testSwitchInCamera() throws UiObjectNotFoundException {
        int switchTimes = 1;
        UiObject slow = UiObjectRid("com.android.camera2:id/mode_slow_motion");
        UiObject video = UiObjectRid("com.android.camera2:id/mode_video");
        UiObject photo = UiObjectRid("com.android.camera2:id/mode_photo");
        UiObject pano = UiObjectRid("com.android.camera2:id/mode_pano");
        ArrayList<UiObject> cameraSanerio = new ArrayList<UiObject>();
        cameraSanerio.add(pano);
        cameraSanerio.add(photo);
        cameraSanerio.add(video);
        cameraSanerio.add(slow);

        swipeToLeft();
        sleepInt(3);
        for (int i = 0; i < switchTimes; i++) {
            for (int j = 0; j < 4; j++) {
                if (!cameraSanerio.get(j).isSelected()) {
                    failed("cannot focused " + cameraSanerio.get(j).getText());
                } else {
                    addInfo(TAG, "focused " + cameraSanerio.get(j).getText());
                }
                swipeToRight();
                sleepInt(3);
            }

            for (int k = 3; k >= 0; k--) {
                if (!cameraSanerio.get(k).isSelected()) {
                    failed("cannot focused " + cameraSanerio.get(k).getText());
                } else {
                    addInfo(TAG, "focused " + cameraSanerio.get(k).getText());
                }
                swipeToLeft();
                sleepInt(3);
            }
        }

    }
    
    public int checkPhoto() {
        int num = 0;
        File f = new File("/mnt/sdcard/DCIM/Camera");
        if (f.isDirectory()) {
            File[] files = f.listFiles();
            num = files.length;
        }
        return num;
    }

    public UiWatcher saveModeWatcher = new UiWatcher() {

        @Override
        public boolean checkForCondition() {
            UiObject saveMode = UiObjectRid("com.android.camera2:id/dialog_btn");
            if (saveMode.exists()) {
                try {
                    addInfo(TAG, "save mode display");
                    saveMode.click();
                } catch (UiObjectNotFoundException e) {
                    e.printStackTrace();
                }
                sleepInt(1);
            }
            return true;
        }

    };
}

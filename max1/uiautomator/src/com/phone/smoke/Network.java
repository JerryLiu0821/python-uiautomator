package com.phone.smoke;

import com.android.uiautomator.core.UiObject;
import com.android.uiautomator.core.UiObjectNotFoundException;

public class Network extends BaseCase {

    private final static String TAG = "NetWork";

    /*
     * connect letv-office
     */
    public void testConnectWifi() throws UiObjectNotFoundException {
        String wifi = "letv-office";

        press_Home(2, 1);
        UiObject sett = UiObjectText("设置");
        sett.click();
        sleepInt(2);

        UiObject wlan = UiObjectText("WLAN");
        int wlanTimes = 0;
        for(; wlanTimes < 5; wlanTimes++){
            if(!wlan.exists()){
                sett.click();
                sleepInt(2);
            }else{
                break;
            }
        }
        if(wlanTimes == 5 && !wlan.exists()){
            failed("cannot enter settings");
        }
        wlan.click();
        sleepInt(1);


        UiObject wifiList = UiObjectRid("android:id/list");
        if (!wifiList.exists()) {
            addInfo(TAG, "wifi is not open, open it");
            UiObjectRid("com.android.settings:id/switch_text").click();
            sleepInt(5);
            if (!wifiList.exists()) {
                failed("open wifi failed");
            }
        }

        UiObject letvOffice = UiObjectText(wifi);
        if (!letvOffice.exists()) {

        }
        letvOffice.click();
        sleepInt(2);
        UiObject conti = UiObjectRid("com.baidu.input_letv:id/dialog_continue");
        if (conti.exists()) {
            conti.click();
            addInfo(TAG, "click baidu");
            sleepInt(1);
        }
        sleepInt(2);
        UiObject pwdEditBox = UiObjectRid("android:id/le_edit_text_content");
        addInfo(TAG, "click editbox");
        pwdEditBox.click();
        sleepInt(2);
        UiObject isConnect = UiObjectRid("android:id/summary");
        if (wifiList.exists() && !isConnect.exists()) {
            letvOffice.click();
            sleepInt(3);
        }
        pwdEditBox.exists();
        pwdEditBox.setText("987654321");
        sleepInt(3);
        
        UiObjectRid("android:id/button1").click();
        sleepInt(8);
        if (isConnect.exists()) {
            if (isConnect.getText().equals("已连接")) {
                addInfo(TAG, "已连接 " + wifi);
            } else {
                failed("未连接到 " + wifi);
            }
        }

        press_Back(3, 1);

    }
}

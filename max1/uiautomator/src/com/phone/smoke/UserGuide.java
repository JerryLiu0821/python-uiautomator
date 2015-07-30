package com.phone.smoke;

import android.os.RemoteException;

import com.android.uiautomator.core.UiObjectNotFoundException;

public class UserGuide extends BaseCase {
    public String TAG = "UserGuide";
    
    public void testSkilUserGuide() throws RemoteException, UiObjectNotFoundException{
        
        
        UiObjectRid("com.letv.android.setupwizard:id/language_simple_chinese").click();
        UiObjectRid("com.letv.android.setupwizard:id/footer_center_button").clickAndWaitForNewWindow();
        sleepInt(1);
        UiObjectRid("com.letv.android.setupwizard:id/footer_center_button").clickAndWaitForNewWindow();
        sleepInt(2);
        UiObjectRid("com.android.settings:id/footer_center_button").clickAndWaitForNewWindow();
        sleepInt(1);
        UiObjectRid("com.letv.android.setupwizard:id/footer_center_button").clickAndWaitForNewWindow();
        sleepInt(1);
        UiObjectRid("com.letv.android.setupwizard:id/footer_center_button").clickAndWaitForNewWindow();
        sleepInt(1);
        UiObjectRid("com.letv.android.setupwizard:id/footer_center_button").clickAndWaitForNewWindow();
        sleepInt(1);
        UiObjectRid("com.letv.android.setupwizard:id/footer_center_button").clickAndWaitForNewWindow();
        sleepInt(5);
        
        
        
        addInfo(TAG, "click finished");
    }
}

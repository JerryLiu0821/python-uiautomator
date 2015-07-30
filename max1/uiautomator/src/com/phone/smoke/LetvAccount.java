package com.phone.smoke;

import com.android.uiautomator.core.UiObject;
import com.android.uiautomator.core.UiObjectNotFoundException;
import com.android.uiautomator.core.UiSelector;

public class LetvAccount extends BaseCase {

    /*
     * login letv account
     */
    public void testLoginAccount() throws UiObjectNotFoundException {
        String TAG = "account";
        press_Home(2, 1);
        UiObjectText("设置").clickAndWaitForNewWindow();
        sleepInt(1);
        UiObject accountManager = UiObjectText("帐号管理");
        if (!accountManager.exists()) {
            swipeToBottom();
            sleepInt(1);
        }
        accountManager.click();
        sleepInt(1);
        UiObjectText("添加帐户").click();
        sleepInt(1);
        UiObjectText("乐视帐号").click();
        sleepInt(2);
        UiObject hasAccountObject = UiObjectRid("com.letv.android.account:id/btn_login");
        hasAccountObject.click();
        sleepInt(2);

        UiObject username = UiObjectRid("com.letv.android.account:id/username");
        UiObject account = username.getChild(new UiSelector().index(0))
                .getChild(new UiSelector().index(1))
                .getChild(new UiSelector().index(0));
        UiObject passwd = UiObjectText("6-16位的密码");
        UiObject login = UiObjectText("登陆");
        account.click();
        sleepInt(1);
        account.setText("15901023880");
        press_Back(1, 1);
        passwd.click();
        sleepInt(1);
        passwd.setText("010238");
        press_Back(1, 1);
        login.click();
        sleepInt(8);
        if (UiObjectText("退出帐号").exists()) {
            addInfo(TAG, "登陆成功");
        } else {
            failed("登陆失败");
        }
    }

    public void tearDown() throws Exception {
        super.tearDown();
        press_Back(5, 1);
    }

}

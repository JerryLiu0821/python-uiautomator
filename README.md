# 总述
该程序是python写的用来运行uiautomator并最终生成html结果的框架

# 使用说明
```
Usage: myloader.py [options]

Options:
  -h, --help            show this help message and exit
  -f LISTFILE, --file=LISTFILE
                        case or list to run
  -s SERIALNO, --serial=SERIALNO
                        which device to run
  -c COUNT, --count=COUNT
                        how many times to run
  -r REPORTDIR, --reportdir=REPORTDIR
                        where to capture report
  -j JARPATH, --jar=JARPATH
                        which jar to run

```

# 详细说明

## -f 详解
1. -f 用来指定需要运行的用例列表，可以是一个list文件，或者是一条格式化的list语句， 例如：

>smoke.com.phone.smoke.LeJian#testLeJianPerformance

>smoke: 运行的jar名

>com.phone.smoke.LeJian#testLeJianPerformance: 具体的用例名

2. -s 指定设备序列号，通过`adb devices`获取，当机器只连接一个设备的时候可以不用指定，但连接多个时，必须指定

3. -j 指定需要运行push到手机中的jar包

4. -r 指定报告生成的路径，最终结果时在该路径下的logs/result开头的文件夹中

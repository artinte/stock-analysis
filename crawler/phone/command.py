import os
import re
import time
import random
import subprocess
import pathlib
import datetime


def check_adb():
    search_list = ["adb", "adb.bat"]
    with open(os.devnull, "w") as devnull:
        for adb in search_list:
            try:
                subprocess.run(
                    [adb, "version"], stdout=devnull, stderr=devnull, check=False
                )
                return True
            except FileNotFoundError:
                continue
        return False


def print_adb_version():
    try:
        result = subprocess.run(
            ["adb", "version"], capture_output=True, text=True, check=True
        )
        print(result.stdout.strip())
    except subprocess.CalledProcessError as e:
        print(e)


def get_serials():
    result = {}
    ret = subprocess.run(
        ["adb", "devices"], stdout=subprocess.PIPE, text=True, check=True
    )
    if ret.returncode == 0:
        lines = ret.stdout.split("\n")
        for line in lines:
            temp = re.split(r"[\s\t]+", line)
            if len(temp) != 2:
                continue
            result[temp[0]] = temp[1].lower()
    return result


def is_screen_awake(uuid):
    try:
        result = subprocess.run(
            ["adb", "-s", uuid, "shell", "dumpsys", "power"],
            capture_output=True,
            text=True,
            check=True,
        )
        awake = "mWakefulness=Awake" in result.stdout
        screen_on = (
            "mDisplayPowerState=ON" in result.stdout
            or "Display Power: state=ON" in result.stdout
            or "mScreenOn=true" in result.stdout
            or "mHoldingDisplaySuspendBlocker=true" in result.stdout
            or re.search(r"Display.*state=ON", result.stdout) is not None
        )

        return awake and screen_on
    except subprocess.CalledProcessError:
        print("程序异常")
        return False


def phone_power(uuid, on=True, timeout=10):
    is_awake_initial = is_screen_awake(uuid)
    print(
        f"{uuid} {datetime.datetime.now()} 初始屏幕状态: {'亮屏' if is_awake_initial else '熄屏'}"
    )

    if on == is_awake_initial:
        print(f"屏幕状态已是 {'亮屏' if on else '熄屏'}，无需切换")
        return

    # 轮询检查，直到屏幕状态符合预期或超时
    start_time = time.time()
    while True:
        subprocess.run(["adb", "-s", uuid, "shell", "input", "keyevent", "26"])
        time.sleep(random.uniform(1.5, 2.5))
        current_awake_state = is_screen_awake(uuid)
        if on == current_awake_state:
            print(f"屏幕状态已成功切换为 {'亮屏' if on else '熄屏'}")
            return
        else:
            print("继续发送电源指令")
            if on:
                subprocess.run(["adb", "-s", uuid, "shell", "input", "keyevent", "82"])
                time.sleep(1)
                subprocess.run(["adb", "-s", uuid, "shell", "input", "keyevent", "3"])
                time.sleep(1)

        if time.time() - start_time > timeout:
            print(f"屏幕状态切换超时，期望状态为 {'亮屏' if on else '熄屏'}")
            return


def phone_size(uuid):
    ret = subprocess.run(
        ["adb", "-s", uuid, "shell", "wm", "size"], stdout=subprocess.PIPE
    )
    if ret.returncode == 0:
        decoded_data = ret.stdout.decode("utf-8")
        match = re.search(r"(\d+)x(\d+)", decoded_data)
        if match:
            width, height = match.groups()
            print(f"Phone {uuid} size: {width}x{height}")
            return (int(width), int(height))
    return (0, 0)


def swipe_up(uuid, width, height, interval=10):
    x1 = width // 2 + random.randint(-20, 20)
    x2 = width // 2 + random.randint(-20, 20)
    y1 = height // 2 + random.randint(-20, 20)
    y2 = height // 4 + random.randint(-20, 20)
    duration = random.randint(100, 500)
    subprocess.run(
        [
            "adb",
            "-s",
            uuid,
            "shell",
            "input",
            "swipe",
            str(x1),
            str(y1),
            str(x2),
            str(y2),
            str(duration),
        ]
    )
    print(f"Phone {uuid} swipe up: ({x1}, {y1}) ({x2}, {y2})")
    if interval > 0:
        time.sleep(random.randint(-3, 3) + interval)


def swipe_left(uuid, width, height, interval=10):
    x1 = width * 3 // 4 + random.randint(-20, 20)
    x2 = width // 4 + random.randint(-20, 20)
    y1 = height // 2 + random.randint(-20, 20)
    y2 = height // 2 + random.randint(-20, 20)
    duration = random.randint(100, 500)
    subprocess.run(
        [
            "adb",
            "-s",
            uuid,
            "shell",
            "input",
            "swipe",
            str(x1),
            str(y1),
            str(x2),
            str(y2),
            str(duration),
        ]
    )
    print(f"Phone {uuid} swipe left: ({x1}, {y1}) ({x2}, {y2})")
    if interval > 0:
        time.sleep(random.randint(-3, 3) + interval)


def unlock_swipe(uuid, width, height, interval=2):
    """用于消除锁屏界面的专用滑动，从底部滑到顶部。"""
    x = width // 2
    y_start = int(height * 0.8)  # 底部 80%
    y_end = int(height * 0.2)  # 顶部 20%
    duration_ms = 300  # 快速滑动

    subprocess.run(
        [
            "adb",
            "-s",
            uuid,
            "shell",
            "input",
            "swipe",
            str(x),
            str(y_start),
            str(x),
            str(y_end),
            str(duration_ms),
        ]
    )
    if interval > 0:
        time.sleep(interval)


def tap(uuid, x, y, interval=8):
    subprocess.run(["adb", "-s", uuid, "shell", "input", "tap", str(x), str(y)])
    print(f"Phone {uuid} tap: {x} {y}")
    if interval > 0:
        time.sleep(interval + random.randint(-2, 2))


def back(uuid, interval=5):
    """
    执行 ADB 返回 (Back) 命令，并暂停一段时间。

    Args:
        uuid (str): 设备的序列号。
        interval (int, optional): 命令执行后暂停的基础秒数。默认 8 秒。
    """
    # ADB keyevent 4 对应 'Back' 键
    subprocess.run(["adb", "-s", uuid, "shell", "input", "keyevent", "4"])
    print(f"Phone {uuid} executed: BACK command (keyevent 4)")
    if interval > 0:
        # 暂停时间加上随机抖动，模拟人类行为
        sleep_time = interval + random.randint(0, 1)
        # 确保暂停时间不为负
        time.sleep(max(1, sleep_time))


def lanuch_app(uuid, activity, interval=8):
    subprocess.run(["adb", "-s", uuid, "shell", "am", "start", activity])
    if interval > 0:
        time.sleep(interval + random.randint(-1, 1))


def lanuch_app_with_intent(uuid, package_name, interval=8):
    subprocess.run(
        [
            "adb",
            "-s",
            uuid,
            "shell",
            "monkey",
            "-p",
            package_name,
            "-c",
            "android.intent.category.LAUNCHER",
            "1",
        ]
    )
    if interval > 0:
        time.sleep(interval + random.randint(-1, 1))


def close_app(uuid, activity, interval=4):
    package_name = activity.split("/")[0]
    subprocess.run(["adb", "-s", uuid, "shell", "am", "force-stop", package_name])
    if interval > 0:
        time.sleep(interval + random.randint(-1, 1))


def close_all_apps(uuid, activity=None):
    """
    通过 ADB 清空所有后台进程，并强制停止一个指定的前台应用。

    Args:
        uuid (str): 设备的序列号。
        activity (str, optional): 需要额外强制停止的应用 Activity 字符串。
                                   格式通常为 'package_name/main_activity'。
    """

    # 1. 停止所有后台进程
    try:
        print(f"[{uuid}] 正在停止所有后台应用进程...")
        # am kill-all-processes: 停止所有非持久性的后台进程
        # 注意：此命令不保证能停止所有前台或持久性服务。
        result = subprocess.run(
            ["adb", "-s", uuid, "shell", "am", "kill-all-processes"],
            capture_output=True,
            text=True,
            check=True,
        )
        # 不同的 Android 版本可能命令略有差异
        print(f"[{uuid}] 后台进程清理命令执行完毕。")

    except subprocess.CalledProcessError as e:
        error_output = e.stderr.strip() if e.stderr else "（无标准错误信息）"
        if e.stdout.strip():
            error_output += f"; stdout包含信息: {e.stdout.strip()}"
        print(f"[{uuid}] am kill-all-processes 命令执行失败 错误信息: {error_output}")
    except FileNotFoundError:
        print("错误: 找不到 ADB 命令，请确认环境变量设置正确。")
        return

    # 2. (可选) 强制停止指定的前台应用
    if activity:
        package_name = activity.split("/")[0]
        try:
            print(f"[{uuid}] 正在强制停止指定应用: {package_name}...")
            # am force-stop: 彻底杀死指定包名的应用
            subprocess.run(
                ["adb", "-s", uuid, "shell", "am", "force-stop", package_name],
                check=True,
                capture_output=True,
            )
            print(f"[{uuid}] 应用 {package_name} 强制停止成功。")
        except subprocess.CalledProcessError as e:
            print(
                f"[{uuid}] 错误: 强制停止应用 {package_name} 失败。错误信息: {e.stderr.strip()}"
            )
            return

    # 3. 增加延时，确保系统稳定
    sleep_time = random.randint(3, 5)
    print(f"[{uuid}] 暂停 {sleep_time} 秒等待系统稳定...")
    time.sleep(sleep_time)


def take_screenshot(uuid, local_dir=None):
    device_path = "/sdcard/screen.png"

    filename = f"{uuid}_screen.png"
    if local_dir:
        local_path = pathlib.Path(local_dir) / filename
    else:
        local_path = pathlib.Path.home() / "Pictures" / filename
    local_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        # 进行截图
        subprocess.run(
            ["adb", "-s", uuid, "shell", "screencap", "-p", device_path],
            check=True,
            capture_output=True,
        )
        # 传递到电脑上
        subprocess.run(
            ["adb", "-s", uuid, "pull", device_path, local_path],
            check=True,
            capture_output=True,
        )

    except Exception as e:
        print(e)


def check_app_exist(uuid, package_name):
    try:
        result = subprocess.run(
            ["adb", "-s", uuid, "shell", "pm", "list", "packages", package_name],
            capture_output=True,
            text=True,
            timeout=5,
        )

        if result.returncode == 0:
            return f"package:{package_name}" in result.stdout.strip().splitlines()
        return False

    except Exception as e:
        print(f"检查应用 {package_name} 时发生错误: {e}")
        return False


def package_list(uuid):
    try:
        result = subprocess.run(
            ["adb", "-s", uuid, "shell", "pm", "list", "packages"],
            capture_output=True,
            text=True,
            timeout=5,
        )

        packages = []
        if result.returncode == 0:
            lines = result.stdout.strip().splitlines()
            for line in lines:
                if line.startswith("package:"):
                    packages.append(line[len("package:") :])
        return packages

    except Exception as e:
        print(f"获取应用列表时发生错误: {e}")
        return []

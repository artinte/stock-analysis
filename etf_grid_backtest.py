from dotenv import dotenv_values
from gateways.data_manager import DataManager

def main():
    config = dotenv_values("private_config.txt")
    dm = DataManager(provider_name="yinhe")
    
    if dm.start(config):
        try:
            pass
        except Exception as e:
            print("数据获取失败：", e)
        finally:
            dm.stop()


if __name__ == "__main__":
    main()

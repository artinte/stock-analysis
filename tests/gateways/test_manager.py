from gateways.manager import DataManager


def main() -> None:
    print("【DataManager 测试】")

    try:
        providers = DataManager.available_providers()

        print("已注册数据源：")

        for provider in providers:
            print(f"  • {provider}")

    except Exception as exc:
        print(f"❌ 获取数据源失败：{exc}")
        return

    if not providers:
        print("⚠️ 当前没有注册任何数据源")
        return

    for provider_name in providers:
        print()
        print(f"测试数据源：{provider_name}")

        data = None

        try:
            data = DataManager(provider_name)

            print(f"Provider：{data.provider}")

            data.start()

            print("✅ start()")

            healthy = data.health_check()

            if healthy:
                print("✅ health_check()")
            else:
                print("❌ health_check()")

        except Exception as exc:
            print(f"❌ DataManager 测试失败：{exc}")

        finally:
            if data is not None:
                try:
                    data.stop()
                    print("✅ stop()")
                except Exception as exc:
                    print(f"⚠️ stop() 失败：{exc}")


if __name__ == "__main__":
    main()

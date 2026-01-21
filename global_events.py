class GlobalEvent:
    """
    用于记录全球重大事件及其对 A 股市场的潜在影响的数据结构。

    属性:
        date (str): 事件发生的日期 (例如: '2025-12-05')。
        title (str): 事件的标题或名称。
        description (str): 对事件的详细描述或背景。
        current_a_share_index (float): 事件发生时的 A 股指数（如上证指数）点位。
        a_share_index_change_impact (float): 市场对该事件的预期指数影响值（例如: +0.2 或 -15.0）。
    """

    def __init__(
        self,
        date: str,
        title: str,
        url: str,
        current_a_share_index: float,
        a_share_index_change_impact: float,
    ):
        """
        初始化一个 GlobalEvent 实例。

        参数:
            date (str): 事件发生的日期。
            title (str): 事件的标题。
            url (str): 事件的引用链接。
            current_a_share_index (float): 事件发生时的指数点位。
            a_share_index_change_impact (float): 预期指数影响值。
            description (str, optional): 对事件的详细描述。
        """
        self.date = date
        self.title = title
        self.url = url,
        self.current_a_share_index = current_a_share_index
        self.a_share_index_change_impact = a_share_index_change_impact

GlobalEventsList = [
    GlobalEvent(
        date="2025-12-05",
        title="国家金融监督管理总局发布《关于调整保险公司相关业务风险因子的通知》",
        url="https://example.com/financial-regulation-2025",
        current_a_share_index = 3902.81,
        a_share_index_change_impact = 27.02,
    ),
]

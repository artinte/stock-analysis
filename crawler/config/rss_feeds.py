from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import quote

# ============================================================
# RSSFeed
# ============================================================


@dataclass(frozen=True, slots=True)
class RSSFeed:
    """
    RSS 数据源配置。

    这里只描述 RSS 数据源本身，
    不负责抓取、重试、并发。

    抓取策略由 RSSFeedSpider / RSSFeedManager 负责。
    """

    # ============================================================
    # 基本信息
    # ============================================================

    name: str
    url: str

    # 新闻分类
    category: str = "财经"

    # 数据源描述
    description: str = ""

    # ============================================================
    # 数据源状态
    # ============================================================

    # 是否启用
    enabled: bool = True

    # 数据源优先级
    #
    # 1 = 核心
    # 2 = 重要
    # 3 = 普通
    priority: int = 3

    # ============================================================
    # 数据源元信息
    # ============================================================

    # RSS 内容语言
    #
    # 例如：
    #   zh-CN
    #   zh-TW
    #   en-US
    language: str = "zh-CN"

    # 数据源所属地区
    #
    # 例如：
    #   CN
    #   TW
    #   US
    #   GB
    region: str = ""

    # 数据源类型
    #
    # search   = 搜索型 RSS
    # category = 分类 RSS
    # site     = 网站 RSS
    # topic    = 主题 RSS
    source_type: str = "site"

    # 标签
    #
    # 用于后续：
    #
    #   股票
    #   A股
    #   港股
    #   美股
    #   宏观
    #   科技
    #
    tags: tuple[str, ...] = ()

    # ============================================================
    # 授权 / 来源信息
    # ============================================================

    # 来源 / 授权说明
    license: str = ""

    # 是否要求保留来源署名
    attribution_required: bool = False

    # ============================================================
    # 抓取参数
    # ============================================================

    # 单个 RSS 最大新闻数量
    max_items: int | None = 50

    # HTTP 超时时间
    timeout: int = 15


# ============================================================
# 经济观察网
# ============================================================
#
# 经济观察网官方 RSS 页面提供多个频道。
#
# 重点：
#   政经要闻
#   金融投资
#   公司产业
#   观察家
#   首页
#   专题
#   今日头条
#
# ============================================================

EEO_FEEDS: list[RSSFeed] = [
    RSSFeed(
        name="经济观察网",
        url=("http://www.eeo.com.cn/" "sypd/rss.xml"),
        category="财经",
        description="经济观察网首页新闻",
        priority=1,
        license="经济观察网 RSS",
    ),
    RSSFeed(
        name="经济观察网政经",
        url=("http://www.eeo.com.cn/" "Politics/rss.xml"),
        category="宏观政策",
        description="经济观察网政经要闻",
        priority=1,
        license="经济观察网 RSS",
    ),
    RSSFeed(
        name="经济观察网金融",
        url=("http://www.eeo.com.cn/" "finance/rss.xml"),
        category="金融",
        description="经济观察网金融投资频道",
        priority=1,
        license="经济观察网 RSS",
    ),
    RSSFeed(
        name="经济观察网公司产业",
        url=("http://www.eeo.com.cn/" "industry/rss.xml"),
        category="公司产业",
        description="经济观察网公司与产业新闻",
        priority=1,
        license="经济观察网 RSS",
    ),
    RSSFeed(
        name="经济观察网观察家",
        url=("http://www.eeo.com.cn/" "observer/rss.xml"),
        category="观点",
        description="经济观察网观察家栏目",
        priority=2,
        license="经济观察网 RSS",
    ),
    RSSFeed(
        name="经济观察网今日媒体",
        url=("http://www.eeo.com.cn/" "today_media/rss.xml"),
        category="财经资讯",
        description="经济观察网今日媒体",
        priority=2,
        license="经济观察网 RSS",
    ),
    RSSFeed(
        name="经济观察网专题",
        url=("http://www.eeo.com.cn/" "sypd/sdbd/rss.xml"),
        category="专题",
        description="经济观察网专题报道",
        priority=2,
        license="经济观察网 RSS",
    ),
    RSSFeed(
        name="经济观察网今日头条",
        url=("http://www.eeo.com.cn/" "sypd/jrtt/rss.xml"),
        category="重要新闻",
        description="经济观察网今日头条",
        priority=1,
        license="经济观察网 RSS",
    ),
]


# ============================================================
# 合并
# ============================================================

CHINESE_FINANCE_FEEDS: list[RSSFeed] =  EEO_FEEDS


# ============================================================
# Google News
# ============================================================


GOOGLE_NEWS_SEARCH = "https://news.google.com/rss/search"


def google_news(
    name: str,
    query: str,
    category: str,
    *,
    description: str = "",
    priority: int = 1,
    tags: tuple[str, ...] = (),
    enabled: bool = True,
) -> RSSFeed:
    """
    创建 Google News 搜索 RSS。

    默认：
        中国
        简体中文
    """

    url = (
        f"{GOOGLE_NEWS_SEARCH}"
        f"?q={quote(query)}"
        f"&hl=zh-CN"
        f"&gl=CN"
        f"&ceid=CN:zh-Hans"
    )

    return RSSFeed(
        name=name,
        url=url,
        category=category,
        description=description,
        enabled=enabled,
        priority=priority,
        language="zh-CN",
        region="CN",
        source_type="search",
        tags=tags,
        license="Google News RSS",
        attribution_required=True,
    )


# ============================================================
# 中国新闻网
#
# 官方 RSS：
#
#   即时新闻
#   要闻
#   国内
#   国际
#   财经
#   IT
#   房产
#   汽车
#   台湾
#   军事
# ============================================================


CHINANEWS_FEEDS: list[RSSFeed] = [
    RSSFeed(
        name="中国新闻网财经",
        url=("https://www.chinanews.com.cn/" "rss/finance.xml"),
        category="财经",
        description="中国新闻网财经新闻",
        priority=1,
        language="zh-CN",
        region="CN",
        source_type="official",
        tags=("财经", "宏观", "A股"),
        license="中国新闻网 RSS",
    ),
    RSSFeed(
        name="中国新闻网即时",
        url=("https://www.chinanews.com.cn/" "rss/scroll-news.xml"),
        category="综合新闻",
        description="中国新闻网即时新闻",
        priority=2,
        language="zh-CN",
        region="CN",
        source_type="official",
        tags=("新闻", "宏观"),
        license="中国新闻网 RSS",
    ),
    RSSFeed(
        name="中国新闻网要闻",
        url=("https://www.chinanews.com.cn/" "rss/importnews.xml"),
        category="重要新闻",
        description="中国新闻网要闻导读",
        priority=2,
        language="zh-CN",
        region="CN",
        source_type="official",
        tags=("新闻", "宏观", "政策"),
        license="中国新闻网 RSS",
    ),
    RSSFeed(
        name="中国新闻网国内",
        url=("https://www.chinanews.com.cn/" "rss/china.xml"),
        category="国内",
        description="中国新闻网国内新闻",
        priority=2,
        language="zh-CN",
        region="CN",
        source_type="official",
        tags=("国内", "政策", "宏观"),
        license="中国新闻网 RSS",
    ),
    RSSFeed(
        name="中国新闻网国际",
        url=("https://www.chinanews.com.cn/" "rss/world.xml"),
        category="国际",
        description="中国新闻网国际新闻",
        priority=2,
        language="zh-CN",
        region="CN",
        source_type="official",
        tags=("国际", "宏观"),
        license="中国新闻网 RSS",
    ),
    RSSFeed(
        name="中国新闻网IT",
        url=("https://www.chinanews.com.cn/" "rss/it.xml"),
        category="科技",
        description="中国新闻网 IT 科技新闻",
        priority=1,
        language="zh-CN",
        region="CN",
        source_type="official",
        tags=("科技", "AI", "半导体"),
        license="中国新闻网 RSS",
    ),
    RSSFeed(
        name="中国新闻网房产",
        url=("https://www.chinanews.com.cn/" "rss/estate.xml"),
        category="房地产",
        description="中国新闻网房地产新闻",
        priority=2,
        language="zh-CN",
        region="CN",
        source_type="official",
        tags=("房地产", "地产"),
        license="中国新闻网 RSS",
    ),
    RSSFeed(
        name="中国新闻网汽车",
        url=("https://www.chinanews.com.cn/" "rss/auto.xml"),
        category="汽车",
        description="中国新闻网汽车行业新闻",
        priority=2,
        language="zh-CN",
        region="CN",
        source_type="official",
        tags=("汽车", "新能源车"),
        license="中国新闻网 RSS",
    ),
    RSSFeed(
        name="中国新闻网台湾",
        url=("https://www.chinanews.com.cn/" "rss/taiwan.xml"),
        category="台湾",
        description="中国新闻网台湾新闻",
        priority=3,
        language="zh-CN",
        region="CN",
        source_type="official",
        tags=("台湾", "台股"),
        license="中国新闻网 RSS",
    ),
]


# ============================================================
# Yahoo Taiwan
#
# Yahoo 官方提供：
#
#   最新新聞
#   台股動態
#   國際財經
#   小資理財
#   基金動態
#   專家專欄
#   研究報導
#
# ============================================================


YAHOO_TW_FEEDS: list[RSSFeed] = [
    RSSFeed(
        name="Yahoo台股",
        url=("https://tw.stock.yahoo.com/rss" "?category=tw-market"),
        category="台股",
        description="Yahoo 股市台股市場動態",
        priority=1,
        language="zh-TW",
        region="TW",
        source_type="official",
        tags=("台股", "股票", "半導體"),
        license="Yahoo 股市 RSS",
    ),
    RSSFeed(
        name="Yahoo台湾财经",
        url=("https://tw.stock.yahoo.com/rss" "?category=news"),
        category="台湾财经",
        description="Yahoo 股市最新財經新聞",
        priority=1,
        language="zh-TW",
        region="TW",
        source_type="official",
        tags=("台股", "财经"),
        license="Yahoo 股市 RSS",
    ),
    RSSFeed(
        name="Yahoo国际财经",
        url=("https://tw.stock.yahoo.com/rss" "?category=intl-markets"),
        category="国际财经",
        description="Yahoo 股市國際財經",
        priority=2,
        language="zh-TW",
        region="TW",
        source_type="official",
        tags=("国际", "美股", "全球"),
        license="Yahoo 股市 RSS",
    ),
    RSSFeed(
        name="Yahoo基金",
        url=("https://tw.stock.yahoo.com/rss" "?category=funds-news"),
        category="基金",
        description="Yahoo 股市基金動態",
        priority=2,
        language="zh-TW",
        region="TW",
        source_type="official",
        tags=("基金", "ETF"),
        license="Yahoo 股市 RSS",
    ),
    RSSFeed(
        name="Yahoo研究报告",
        url=("https://tw.stock.yahoo.com/rss" "?category=research"),
        category="研究报告",
        description="Yahoo 股市研究報告",
        priority=2,
        language="zh-TW",
        region="TW",
        source_type="research",
        tags=("研报", "研究报告"),
        license="Yahoo 股市 RSS",
    ),
    RSSFeed(
        name="Yahoo财经专栏",
        url=("https://tw.stock.yahoo.com/rss" "?category=column"),
        category="财经专栏",
        description="Yahoo 股市專家專欄",
        priority=3,
        language="zh-TW",
        region="TW",
        source_type="official",
        tags=("投资", "观点"),
        license="Yahoo 股市 RSS",
    ),
    RSSFeed(
        name="Yahoo个人理财",
        url=("https://tw.stock.yahoo.com/rss" "?category=personal-finance"),
        category="个人理财",
        description="Yahoo 股市小資理財",
        priority=3,
        language="zh-TW",
        region="TW",
        source_type="official",
        tags=("理财", "基金", "投资"),
        license="Yahoo 股市 RSS",
    ),
]


# ============================================================
# 中央社 CNA
#
# 官方：
#   產經證券
#   科技
#   國際
#   兩岸
# ============================================================


CNA_FEEDS: list[RSSFeed] = [
    RSSFeed(
        name="中央社产经证券",
        url=("https://feeds.feedburner.com/" "rsscna/finance"),
        category="产经证券",
        description="中央社產經證券新聞",
        priority=1,
        language="zh-TW",
        region="TW",
        source_type="official",
        tags=("台股", "证券", "财经"),
        license="中央社 RSS",
    ),
    RSSFeed(
        name="中央社科技",
        url=("https://feeds.feedburner.com/" "rsscna/technology"),
        category="科技",
        description="中央社科技新聞",
        priority=1,
        language="zh-TW",
        region="TW",
        source_type="official",
        tags=("科技", "AI", "半导体"),
        license="中央社 RSS",
    ),
    RSSFeed(
        name="中央社国际",
        url=("https://feeds.feedburner.com/" "rsscna/intworld"),
        category="国际",
        description="中央社國際新聞",
        priority=2,
        language="zh-TW",
        region="TW",
        source_type="official",
        tags=("国际", "宏观"),
        license="中央社 RSS",
    ),
    RSSFeed(
        name="中央社两岸",
        url=("https://feeds.feedburner.com/" "rsscna/mainland"),
        category="两岸",
        description="中央社兩岸新聞",
        priority=2,
        language="zh-TW",
        region="TW",
        source_type="official",
        tags=("两岸", "中国", "宏观"),
        license="中央社 RSS",
    ),
]


# ============================================================
# Google News
#
# Google 作为“搜索型补充源”
#
# 不代替新浪 / 中新网 / Yahoo 等原始来源。
# ============================================================


GOOGLE_NEWS_FEEDS: list[RSSFeed] = [
    # ------------------------------
    # A股
    # ------------------------------
    google_news(
        "Google-A股",
        "A股",
        "A股",
        description="Google News A股相关新闻",
        priority=1,
        tags=("A股", "股票"),
    ),
    google_news(
        "Google-沪深股市",
        "沪深股市",
        "A股",
        description="Google News 沪深股市",
        priority=1,
        tags=("A股", "沪深"),
    ),
    google_news(
        "Google-上市公司",
        "上市公司",
        "上市公司",
        description="Google News 中国上市公司",
        priority=1,
        tags=("A股", "上市公司"),
    ),
    google_news(
        "Google-IPO",
        "A股 IPO",
        "IPO",
        description="A股 IPO 新闻",
        priority=2,
        tags=("A股", "IPO"),
    ),
    google_news(
        "Google-并购重组",
        "A股 并购重组",
        "并购重组",
        description="A股并购重组新闻",
        priority=2,
        tags=("A股", "并购", "重组"),
    ),
    # ------------------------------
    # 行业
    # ------------------------------
    google_news(
        "Google-半导体",
        "A股 半导体",
        "半导体",
        description="A股半导体产业链",
        priority=1,
        tags=("A股", "半导体", "芯片"),
    ),
    google_news(
        "Google-AI",
        "A股 人工智能",
        "人工智能",
        description="A股人工智能产业链",
        priority=1,
        tags=("A股", "AI", "人工智能"),
    ),
    google_news(
        "Google-机器人",
        "A股 机器人",
        "机器人",
        description="A股机器人产业链",
        priority=2,
        tags=("A股", "机器人"),
    ),
    google_news(
        "Google-商业航天",
        "A股 商业航天",
        "商业航天",
        description="A股商业航天产业链",
        priority=2,
        tags=("A股", "商业航天"),
    ),
    google_news(
        "Google-新能源",
        "A股 新能源",
        "新能源",
        description="A股新能源产业链",
        priority=2,
        tags=("A股", "新能源"),
    ),
    google_news(
        "Google-锂电池",
        "A股 锂电池",
        "锂电池",
        description="A股锂电池产业链",
        priority=2,
        tags=("A股", "锂电", "储能"),
    ),
    google_news(
        "Google-医药",
        "A股 医药",
        "医药",
        description="A股医药行业",
        priority=2,
        tags=("A股", "医药"),
    ),
    google_news(
        "Google-有色金属",
        "A股 有色金属",
        "有色金属",
        description="A股有色金属产业链",
        priority=1,
        tags=("A股", "有色", "资源"),
    ),
    google_news(
        "Google-稀土",
        "A股 稀土",
        "稀土",
        description="A股稀土产业链",
        priority=1,
        tags=("A股", "稀土"),
    ),
    google_news(
        "Google-黄金",
        "A股 黄金",
        "黄金",
        description="黄金及黄金上市公司",
        priority=2,
        tags=("A股", "黄金"),
    ),
    google_news(
        "Google-军工",
        "A股 军工",
        "军工",
        description="A股军工行业",
        priority=2,
        tags=("A股", "军工"),
    ),
    google_news(
        "Google-银行",
        "A股 银行",
        "银行",
        description="A股银行行业",
        priority=2,
        tags=("A股", "银行"),
    ),
    google_news(
        "Google-券商",
        "A股 券商",
        "券商",
        description="A股券商行业",
        priority=2,
        tags=("A股", "券商"),
    ),
    google_news(
        "Google-汽车",
        "A股 汽车",
        "汽车",
        description="A股汽车产业链",
        priority=2,
        tags=("A股", "汽车"),
    ),
    google_news(
        "Google-低空经济",
        "A股 低空经济",
        "低空经济",
        description="A股低空经济",
        priority=2,
        tags=("A股", "低空经济"),
    ),
    # ------------------------------
    # 宏观
    # ------------------------------
    google_news(
        "Google-中国经济",
        "中国经济",
        "宏观经济",
        description="中国宏观经济",
        priority=1,
        tags=("宏观", "中国经济"),
    ),
    google_news(
        "Google-货币政策",
        "中国 货币政策",
        "货币政策",
        description="中国货币政策",
        priority=1,
        tags=("宏观", "央行", "利率"),
    ),
    google_news(
        "Google-财政政策",
        "中国 财政政策",
        "财政政策",
        description="中国财政政策",
        priority=1,
        tags=("宏观", "财政"),
    ),
    google_news(
        "Google-美联储",
        "美联储",
        "全球宏观",
        description="美联储及美国利率",
        priority=1,
        tags=("美联储", "利率", "美元"),
    ),
    google_news(
        "Google-人民币",
        "人民币 汇率",
        "外汇",
        description="人民币汇率",
        priority=2,
        tags=("人民币", "汇率"),
    ),
    google_news(
        "Google-中美贸易",
        "中美贸易",
        "国际贸易",
        description="中美贸易与关税",
        priority=1,
        tags=("中美", "贸易", "关税"),
    ),
    # ------------------------------
    # 大宗商品
    # ------------------------------
    google_news(
        "Google-原油",
        "原油 油价",
        "原油",
        description="国际原油市场",
        priority=1,
        tags=("原油", "能源"),
    ),
    google_news(
        "Google-铜",
        "铜价 铜",
        "铜",
        description="铜价及铜产业链",
        priority=1,
        tags=("铜", "有色"),
    ),
    google_news(
        "Google-铝",
        "铝价 铝",
        "铝",
        description="铝价及铝产业链",
        priority=2,
        tags=("铝", "有色"),
    ),
    google_news(
        "Google-钢铁",
        "钢铁 钢价",
        "钢铁",
        description="钢铁行业",
        priority=2,
        tags=("钢铁", "黑色"),
    ),
    # ------------------------------
    # 港股
    # ------------------------------
    google_news(
        "Google-港股",
        "港股",
        "港股",
        description="香港股票市场",
        priority=1,
        tags=("港股", "香港"),
    ),
    google_news(
        "Google-恒生科技",
        "恒生科技",
        "恒生科技",
        description="恒生科技指数及成分股",
        priority=2,
        tags=("港股", "恒生科技"),
    ),
]


# ============================================================
# 海外财经
#
# 这些源作为英文原始信息源。
# 后续交给 AI 翻译 / 摘要。
# ============================================================


GLOBAL_FEEDS: list[RSSFeed] = [
    RSSFeed(
        name="CNBC",
        url=("https://www.cnbc.com/" "id/100003114/device/rss/rss.html"),
        category="全球财经",
        description="CNBC 全球财经新闻",
        priority=1,
        language="en-US",
        region="US",
        source_type="official",
        tags=("美股", "全球", "宏观"),
        license="CNBC RSS",
    ),
    RSSFeed(
        name="MarketWatch",
        url=("https://feeds.marketwatch.com/" "marketwatch/topstories/"),
        category="全球财经",
        description="MarketWatch 财经市场新闻",
        priority=1,
        language="en-US",
        region="US",
        source_type="official",
        tags=("美股", "市场"),
        license="MarketWatch RSS",
    ),
    RSSFeed(
        name="MarketWatch市场脉搏",
        url=("https://feeds.marketwatch.com/" "marketwatch/marketpulse/"),
        category="美股",
        description="MarketWatch Market Pulse",
        priority=2,
        language="en-US",
        region="US",
        source_type="official",
        tags=("美股", "市场"),
        license="MarketWatch RSS",
    ),
    RSSFeed(
        name="SeekingAlpha",
        url="https://seekingalpha.com/feed.xml",
        category="美股",
        description="Seeking Alpha 投资新闻",
        priority=2,
        language="en-US",
        region="US",
        source_type="official",
        tags=("美股", "投资", "股票"),
        license="Seeking Alpha RSS",
    ),
]


# ============================================================
# 合并所有数据源
# ============================================================


RSS_FEEDS: list[RSSFeed] = [
    # 中国
    *CHINESE_FINANCE_FEEDS,
    *CHINANEWS_FEEDS,
    # 台湾
    *YAHOO_TW_FEEDS,
    *CNA_FEEDS,
    # Google 搜索型
    *GOOGLE_NEWS_FEEDS,
    # 海外
    *GLOBAL_FEEDS,
]


# ============================================================
# 查询接口
# ============================================================


def get_all_feeds() -> list[RSSFeed]:
    """
    获取全部数据源。
    """

    return list(RSS_FEEDS)


def get_enabled_feeds() -> list[RSSFeed]:
    """
    获取所有启用的数据源。
    """

    return [feed for feed in RSS_FEEDS if feed.enabled]


def get_core_feeds() -> list[RSSFeed]:
    """
    获取核心数据源。

    priority == 1
    """

    return [feed for feed in RSS_FEEDS if feed.enabled and feed.priority == 1]


def get_feeds_by_category(
    category: str,
) -> list[RSSFeed]:
    """
    根据分类获取数据源。
    """

    return [feed for feed in RSS_FEEDS if feed.enabled and feed.category == category]


def get_feeds_by_tag(
    tag: str,
) -> list[RSSFeed]:
    """
    根据标签获取数据源。

    示例：

        get_feeds_by_tag("A股")

        get_feeds_by_tag("半导体")

        get_feeds_by_tag("美股")
    """

    return [feed for feed in RSS_FEEDS if feed.enabled and tag in feed.tags]


def get_feeds_by_region(
    region: str,
) -> list[RSSFeed]:
    """
    根据地区获取数据源。

    CN / TW / US
    """

    return [feed for feed in RSS_FEEDS if feed.enabled and feed.region == region]


def get_feeds_by_language(
    language: str,
) -> list[RSSFeed]:
    """
    根据语言获取数据源。

    zh-CN
    zh-TW
    en-US
    """

    return [feed for feed in RSS_FEEDS if feed.enabled and feed.language == language]


def get_feed(
    name: str,
) -> RSSFeed | None:
    """
    根据名称获取 RSS。
    """

    for feed in RSS_FEEDS:

        if feed.name == name:
            return feed

    return None


# ============================================================
# 统计
# ============================================================


def get_feed_statistics() -> dict:
    """
    获取 RSS 数据源统计。

    返回：

        {
            "total": 50,
            "enabled": 45,
            "core": 20,
            "cn": 30,
            "tw": 10,
            "us": 10,
        }
    """

    enabled = get_enabled_feeds()

    return {
        "total": len(RSS_FEEDS),
        "enabled": len(enabled),
        "disabled": (len(RSS_FEEDS) - len(enabled)),
        "core": len([feed for feed in enabled if feed.priority == 1]),
        "important": len([feed for feed in enabled if feed.priority == 2]),
        "extended": len([feed for feed in enabled if feed.priority == 3]),
        "cn": len([feed for feed in enabled if feed.region == "CN"]),
        "tw": len([feed for feed in enabled if feed.region == "TW"]),
        "us": len([feed for feed in enabled if feed.region == "US"]),
    }


def print_feed_summary() -> None:
    """
    打印数据源统计。
    """

    statistics = get_feed_statistics()

    print()
    print("RSS 数据源")
    print()

    print(f"  总数       : " f"{statistics['total']}")

    print(f"  已启用     : " f"{statistics['enabled']}")

    print(f"  核心       : " f"{statistics['core']}")

    print(f"  重要       : " f"{statistics['important']}")

    print(f"  扩展       : " f"{statistics['extended']}")

    print()

    print(f"  中国大陆   : " f"{statistics['cn']}")

    print(f"  台湾       : " f"{statistics['tw']}")

    print(f"  美国       : " f"{statistics['us']}")

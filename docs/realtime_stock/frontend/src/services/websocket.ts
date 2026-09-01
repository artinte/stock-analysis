import type {
  Asset,
  Interval,
  Kline,
  MarketOverview,
  Quote,
  SearchResult,
} from "../types/market";

const API_BASE = "/api";

async function request<T>(
  url: string
): Promise<T> {
  const response = await fetch(url);

  if (!response.ok) {
    throw new Error(
      `HTTP ${response.status}`
    );
  }

  return response.json();
}

export async function fetchQuote(
  symbol: string
): Promise<Quote> {
  try {
    return await request<Quote>(
      `${API_BASE}/quote/${encodeURIComponent(
        symbol
      )}`
    );
  } catch {
    return mockQuote(symbol);
  }
}

export async function fetchKlines(
  symbol: string,
  interval: Interval
): Promise<Kline[]> {
  try {
    return await request<Kline[]>(
      `${API_BASE}/kline/${encodeURIComponent(
        symbol
      )}?interval=${interval}`
    );
  } catch {
    return mockKlines(
      symbol,
      interval
    );
  }
}

export async function fetchMarketOverview(): Promise<MarketOverview> {
  try {
    return await request<MarketOverview>(
      `${API_BASE}/market/overview`
    );
  } catch {
    return mockMarketOverview();
  }
}

export async function searchAssets(
  keyword: string
): Promise<SearchResult[]> {
  if (!keyword.trim()) {
    return [];
  }

  try {
    return await request<SearchResult[]>(
      `${API_BASE}/assets/search?q=${encodeURIComponent(
        keyword
      )}`
    );
  } catch {
    return mockSearch(keyword);
  }
}

function mockQuote(
  symbol: string
): Quote {
  const prices: Record<
    string,
    {
      name: string;
      price: number;
    }
  > = {
    "600519.SH": {
      name: "贵州茅台",
      price: 1482.5,
    },

    "601318.SH": {
      name: "中国平安",
      price: 52.38,
    },

    "300308.SZ": {
      name: "中际旭创",
      price: 186.32,
    },

    "688111.SH": {
      name: "金山办公",
      price: 287.16,
    },

    "688981.SH": {
      name: "中芯国际",
      price: 92.68,
    },
  };

  const item =
    prices[symbol] ?? {
      name: symbol,
      price: 100,
    };

  const prevClose =
    item.price * 0.992;

  const change =
    item.price - prevClose;

  return {
    symbol,

    name: item.name,

    timestamp:
      new Date().toISOString(),

    last_price: item.price,

    prev_close: prevClose,

    open: prevClose * 1.002,

    high: item.price * 1.012,

    low: prevClose * 0.997,

    change,

    change_percent:
      (change / prevClose) * 100,

    volume: 321000,

    amount:
      item.price * 321000,

    turnover: 1.28,

    total_shares: 1250000000,

    circulating_shares: 1100000000,

    market_cap:
      item.price * 1250000000,

    circulating_market_cap:
      item.price * 1100000000,

    amplitude: 1.5,

    average_price:
      item.price * 0.998,

    volume_ratio: 1.18,

    limit_up: item.price * 1.1,

    limit_down: item.price * 0.9,

    status: "trading",

    source: "mock",
  };
}

function mockKlines(
  symbol: string,
  interval: Interval
): Kline[] {
  const quote =
    mockQuote(symbol);

  const count =
    interval === "1d"
      ? 180
      : interval === "1w"
        ? 120
        : 240;

  const result: Kline[] = [];

  let price =
    quote.last_price * 0.82;

  const now = Date.now();

  const step =
    interval === "1d"
      ? 24 * 60 * 60 * 1000
      : interval === "1w"
        ? 7 * 24 * 60 * 60 * 1000
        : 5 * 60 * 1000;

  for (let i = 0; i < count; i++) {
    const timestamp =
      now -
      (count - i) * step;

    const drift =
      Math.sin(i / 15) * 0.012;

    const random =
      (Math.random() - 0.5) *
      0.025;

    const open = price;

    const close =
      open * (1 + drift + random);

    const high =
      Math.max(open, close) *
      (1 + Math.random() * 0.008);

    const low =
      Math.min(open, close) *
      (1 - Math.random() * 0.008);

    const volume =
      100000 +
      Math.random() * 800000;

    result.push({
      symbol,

      timestamp:
        new Date(timestamp).toISOString(),

      interval,

      open,

      high,

      low,

      close,

      volume,

      amount:
        volume * close,
    });

    price = close;
  }

  return result;
}

function mockMarketOverview(): MarketOverview {
  const symbols = [
    {
      symbol: "000001.SH",
      name: "上证指数",
      price: 3348.12,
    },

    {
      symbol: "399001.SZ",
      name: "深证成指",
      price: 10521.33,
    },

    {
      symbol: "399006.SZ",
      name: "创业板指",
      price: 2154.31,
    },

    {
      symbol: "000688.SH",
      name: "科创50",
      price: 1023.42,
    },

    {
      symbol: "000300.SH",
      name: "沪深300",
      price: 3821.55,
    },
  ];

  return {
    timestamp:
      new Date().toISOString(),

    indices: symbols.map(
      (item) => {
        const prev =
          item.price * 0.994;

        return {
          symbol: item.symbol,

          name: item.name,

          type: "index",

          quote: {
            symbol: item.symbol,

            name: item.name,

            timestamp:
              new Date().toISOString(),

            last_price:
              item.price,

            prev_close: prev,

            open:
              prev * 1.002,

            high:
              item.price * 1.005,

            low:
              prev * 0.998,

            change:
              item.price - prev,

            change_percent:
              ((item.price - prev) /
                prev) *
              100,

            volume: 0,

            amount: 0,

            turnover: 0,
          },
        };
      }
    ),

    advancing_count: 2847,

    declining_count: 1932,

    unchanged_count: 321,

    limit_up_count: 63,

    limit_down_count: 12,
  };
}

function mockSearch(
  keyword: string
): SearchResult[] {
  const assets: SearchResult[] = [
    {
      symbol: "600519.SH",
      name: "贵州茅台",
      type: "stock",
    },

    {
      symbol: "601318.SH",
      name: "中国平安",
      type: "stock",
    },

    {
      symbol: "300308.SZ",
      name: "中际旭创",
      type: "stock",
    },

    {
      symbol: "688111.SH",
      name: "金山办公",
      type: "stock",
    },

    {
      symbol: "688981.SH",
      name: "中芯国际",
      type: "stock",
    },
  ];

  const value =
    keyword.toLowerCase();

  return assets.filter(
    (asset) =>
      asset.symbol
        .toLowerCase()
        .includes(value) ||
      asset.name
        .toLowerCase()
        .includes(value)
  );
}
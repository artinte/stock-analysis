import {
  useMarketStore,
} from "../stores/market";

function formatVolume(
  value: number
): string {
  if (value >= 100000000) {
    return `${(
      value / 100000000
    ).toFixed(2)} 亿`;
  }

  if (value >= 10000) {
    return `${(
      value / 10000
    ).toFixed(2)} 万`;
  }

  return value.toLocaleString(
    "zh-CN"
  );
}

function formatAmount(
  value: number
): string {
  if (value >= 100000000) {
    return `${(
      value / 100000000
    ).toFixed(2)} 亿`;
  }

  if (value >= 10000) {
    return `${(
      value / 10000
    ).toFixed(2)} 万`;
  }

  return value.toLocaleString(
    "zh-CN"
  );
}

export default function QuoteInfo() {
  const quote =
    useMarketStore(
      (state) =>
        state.quote
    );

  if (!quote) {
    return null;
  }

  const items = [
    {
      label: "成交量",
      value: formatVolume(
        quote.volume
      ),
    },

    {
      label: "成交额",
      value: formatAmount(
        quote.amount
      ),
    },

    {
      label: "换手率",
      value:
        quote.turnover !==
        undefined
          ? `${quote.turnover.toFixed(
              2
            )}%`
          : "-",
    },

    {
      label: "振幅",
      value:
        quote.amplitude !==
        undefined
          ? `${quote.amplitude.toFixed(
              2
            )}%`
          : "-",
    },

    {
      label: "量比",
      value:
        quote.volume_ratio !==
        undefined
          ? quote.volume_ratio.toFixed(
              2
            )
          : "-",
    },

    {
      label: "均价",
      value:
        quote.average_price !==
        undefined
          ? quote.average_price.toFixed(
              2
            )
          : "-",
    },

    {
      label: "涨停",
      value:
        quote.limit_up !==
        undefined
          ? quote.limit_up.toFixed(
              2
            )
          : "-",
    },

    {
      label: "跌停",
      value:
        quote.limit_down !==
        undefined
          ? quote.limit_down.toFixed(
              2
            )
          : "-",
    },
  ];

  return (
    <section className="quote-info">
      {items.map((item) => (
        <div
          className="quote-item"
          key={item.label}
        >
          <span>
            {item.label}
          </span>

          <strong>
            {item.value}
          </strong>
        </div>
      ))}
    </section>
  );
}
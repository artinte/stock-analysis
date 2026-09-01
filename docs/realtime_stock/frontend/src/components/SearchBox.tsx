import {
  useEffect,
  useRef,
  useState,
} from "react";

import {
  searchAssets,
} from "../services/api";

import {
  useMarketStore,
} from "../stores/market";

import type {
  SearchResult,
} from "../types/market";

export default function SearchBox() {
  const [
    keyword,
    setKeyword,
  ] = useState("");

  const [
    results,
    setResults,
  ] = useState<SearchResult[]>(
    []
  );

  const [
    loading,
    setLoading,
  ] = useState(false);

  const inputRef =
    useRef<HTMLInputElement>(null);

  const setCurrentAsset =
    useMarketStore(
      (state) =>
        state.setCurrentAsset
    );

  useEffect(() => {
    const timer =
      window.setTimeout(
        async () => {
          if (!keyword.trim()) {
            setResults([]);

            return;
          }

          setLoading(true);

          try {
            const data =
              await searchAssets(
                keyword
              );

            setResults(data);
          } finally {
            setLoading(false);
          }
        },
        250
      );

    return () =>
      window.clearTimeout(timer);
  }, [keyword]);

  useEffect(() => {
    const handleKeyDown = (
      event: KeyboardEvent
    ) => {
      if (
        (event.ctrlKey ||
          event.metaKey) &&
        event.key === "k"
      ) {
        event.preventDefault();

        inputRef.current?.focus();
      }

      if (event.key === "Escape") {
        setKeyword("");

        setResults([]);
      }
    };

    window.addEventListener(
      "keydown",
      handleKeyDown
    );

    return () =>
      window.removeEventListener(
        "keydown",
        handleKeyDown
      );
  }, []);

  const selectAsset = (
    asset: SearchResult
  ) => {
    setCurrentAsset(asset);

    setKeyword("");

    setResults([]);
  };

  return (
    <div className="search-wrapper">
      <div className="search-box">
        <span className="search-icon">
          ⌕
        </span>

        <input
          ref={inputRef}
          value={keyword}
          onChange={(event) =>
            setKeyword(
              event.target.value
            )
          }
          placeholder="搜索股票、代码或名称"
        />

        {!keyword && (
          <kbd>⌘ K</kbd>
        )}

        {keyword && (
          <button
            className="search-clear"
            onClick={() => {
              setKeyword("");

              setResults([]);
            }}
          >
            ×
          </button>
        )}
      </div>

      {(results.length > 0 ||
        loading) && (
        <div className="search-results">
          {loading && (
            <div className="search-loading">
              搜索中...
            </div>
          )}

          {results.map(
            (result) => (
              <button
                key={result.symbol}
                className="search-result"
                onClick={() =>
                  selectAsset(
                    result
                  )
                }
              >
                <div>
                  <strong>
                    {result.name}
                  </strong>

                  <span>
                    {result.symbol}
                  </span>
                </div>

                <small>
                  {result.type ===
                  "index"
                    ? "指数"
                    : result.type ===
                        "etf"
                      ? "ETF"
                      : "股票"}
                </small>
              </button>
            )
          )}
        </div>
      )}
    </div>
  );
}
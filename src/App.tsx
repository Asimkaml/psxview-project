import { AlertTriangle, Bell, CalendarClock, Database, RefreshCw, Search } from 'lucide-react';
import { Sidebar } from './components/Sidebar';
import { StockStrip } from './components/StockStrip';
import { PlaceholderPanels } from './components/PlaceholderPanels';
import { useDashboard } from './hooks/useDashboard';

export function App() {
  const { data, error, loading, retry } = useDashboard();

  return (
    <div className="app">
      <Sidebar />

      <main>
        <header className="topbar">
          <label>
            <Search />
            <input
              aria-label="Search PSX companies"
              placeholder="Search a company or symbol"
              disabled
            />
          </label>
          <div className="topActions">
            <button aria-label="Notifications">
              <Bell />
            </button>
            <span className="avatar">AK</span>
          </div>
        </header>

        <div className="content">
          <div className="welcome">
            <div>
              <p className="date">
                <CalendarClock />
                Monday research brief
              </p>
              <h1>Your PSX snapshot, made simple.</h1>
              <p>
                Start with a clean watchlist view and a short stream of
                portfolio-relevant headlines. Detailed evidence and valuation
                tools will arrive later.
              </p>
            </div>

            <div className="marketBadge">
              <span />
              <div>
                <small>PSX market</small>
                <strong>{data?.marketStatus ?? 'Checking…'}</strong>
              </div>
            </div>
          </div>

          <div className="statusbar">
            <div>
              <Database />
              <span>
                <strong>Watchlist overview</strong>
                <small>
                  {data
                    ? `${data.watchlistCount} companies · ${data.asOf}`
                    : 'Loading prototype snapshot…'}
                </small>
              </span>
            </div>

            <button onClick={retry}>
              <RefreshCw />
              Refresh
            </button>
          </div>

          {loading && (
            <div className="loading" aria-live="polite">
              <span />
              <span />
              <span />
            </div>
          )}

          {error && (
            <div className="error" role="alert">
              <AlertTriangle />
              <div>
                <strong>Dashboard data is unavailable</strong>
                <p>{error}</p>
              </div>
              <button onClick={retry}>Try again</button>
            </div>
          )}

          {data && (
            <>
              <StockStrip stocks={data.stocks} />
              <PlaceholderPanels news={data.news} />
            </>
          )}

          <footer className="disclaimer">
            PSXviewAI supports research decisions. It does not provide investment
            advice or guarantee outcomes.
          </footer>
        </div>
      </main>
    </div>
  );
}

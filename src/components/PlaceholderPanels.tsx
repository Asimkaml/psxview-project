import { ExternalLink, Gauge, Newspaper } from 'lucide-react';
import type { NewsItem } from '../types/dashboard';

interface Props {
  news: NewsItem[];
}

function formatRelativeTime(iso: string): string {
  const date = new Date(iso);
  const diffMs = Date.now() - date.getTime();
  const seconds = Math.max(0, Math.floor(diffMs / 1000));

  if (seconds < 60) return 'just now';
  const minutes = Math.floor(seconds / 60);
  if (minutes < 60) return `${minutes}m ago`;
  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `${hours}h ago`;
  const days = Math.floor(hours / 24);
  if (days < 7) return `${days}d ago`;
  return date.toLocaleDateString();
}

export function PlaceholderPanels({ news }: Props) {
  const items = news.slice(0, 4);

  return (
    <div className="panelGrid">
      <section className="panel" aria-labelledby="intel">
        <div className="panelTitle">
          <span>
            <Newspaper />
          </span>
          <div>
            <h2 id="intel">Portfolio news</h2>
            <p>Short headlines linked to your watchlist, no jargon.</p>
          </div>
        </div>

        {items.length === 0 ? (
          <p className="newsEmpty">
            No recent portfolio headlines yet. Add companies to your watchlist to see
            relevant items here.
          </p>
        ) : (
          <ul className="newsList">
            {items.map((item) => (
              <li key={item.id} className="newsItem">
                <p className="newsHeadline">{item.title}</p>
                <p className="newsMeta">
                  {item.source} 
                  {" · "}
                  {formatRelativeTime(item.publishedAt)}
                </p>
              </li>
            ))}
          </ul>
        )}

        <button className="disabledAction" disabled>
          View detailed impact (coming soon)
          <ExternalLink />
        </button>
      </section>

      <section className="panel darkPanel" aria-labelledby="valuation">
        <div className="panelTitle">
          <span>
            <Gauge />
          </span>
          <div>
            <h2 id="valuation">Valuation snapshot</h2>
            <p>Fair-value view for a selected company.</p>
          </div>
        </div>

        <div className="valuationBlank">
          <small>Fair value range</small>
          <strong>Coming soon</strong>
          <p>
            You will see a simple fair-value band once PSXviewAI has verified
            financials and assumptions for a company. Until then, any prices here
            remain illustrative only.
          </p>
        </div>

        <div className="method">
          <span>Method</span>
          <b>Will match each company&apos;s sector</b>
        </div>
      </section>
    </div>
  );
}

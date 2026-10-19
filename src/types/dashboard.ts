export type SourceStatus = 'verified' | 'estimate' | 'stale';

export interface StockSnapshot {
  symbol: string;
  name: string;
  sector: string;
  price: number;
  changePercent: number;
  currency: 'PKR';
  marketTime: string;
  source: string;
  status: SourceStatus;
  spark: number[];
}

export interface NewsItem {
  id: string;
  title: string;
  summary?: string;
  source: string;
  /** ISO-8601 timestamp string */
  publishedAt: string;
  importance: 'high' | 'medium' | 'low';
}

export interface DashboardSummary {
  marketStatus: 'Open' | 'Closed';
  asOf: string;
  watchlistCount: number;
  evidenceCount: number;
  stocks: StockSnapshot[];
  /**
   * Portfolio-relevant news and market intelligence, already filtered for the
   * user's watchlist/holdings. In the general dashboard view this is rendered
   * as a compact list without per-headline ticker clutter.
   */
  news: NewsItem[];
}

export interface DashboardRepository {
  getSummary(signal?: AbortSignal): Promise<DashboardSummary>;
}

export interface DataState {
  mode: 'fixture' | 'api';
  label: string;
}

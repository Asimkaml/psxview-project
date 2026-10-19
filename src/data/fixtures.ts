import type { DashboardSummary } from '../types/dashboard';

// Explicit prototype fixtures: illustrative values, not actual PSX market data.
export const dashboardFixture: DashboardSummary = {
  marketStatus: 'Closed',
  asOf: 'Prototype snapshot · values are illustrative only',
  watchlistCount: 5,
  evidenceCount: 12,
  stocks: [
    {
      symbol: 'MEBL',
      name: 'Meezan Bank',
      sector: 'Commercial banks',
      price: 238.42,
      changePercent: 1.84,
      currency: 'PKR',
      marketTime: 'Illustrative',
      source: 'Prototype fixture',
      status: 'estimate',
      spark: [31, 34, 33, 37, 39, 38, 43],
    },
    {
      symbol: 'FFC',
      name: 'Fauji Fertilizer',
      sector: 'Fertilizer',
      price: 341.18,
      changePercent: 0.72,
      currency: 'PKR',
      marketTime: 'Illustrative',
      source: 'Prototype fixture',
      status: 'estimate',
      spark: [32, 31, 34, 36, 35, 38, 40],
    },
    {
      symbol: 'OGDC',
      name: 'Oil & Gas Dev.',
      sector: 'Exploration',
      price: 219.06,
      changePercent: -0.46,
      currency: 'PKR',
      marketTime: 'Illustrative',
      source: 'Prototype fixture',
      status: 'estimate',
      spark: [42, 40, 41, 38, 39, 36, 35],
    },
  ],
  news: [
    {
      id: 'n1',
      title: 'Illustrative PSX session: banking and fertilizer lead gains',
      summary:
        'Prototype headline about broad-based gains across major PSX sectors.',
      source: 'Prototype news fixture',
      publishedAt: '2024-10-15T09:30:00Z',
      importance: 'medium',
    },
    {
      id: 'n2',
      title: 'Sample monetary policy update with potential impact on banks',
      summary:
        'Example item describing how a rate change could affect sector earnings.',
      source: 'Prototype macro fixture',
      publishedAt: '2024-10-14T14:05:00Z',
      importance: 'high',
    },
    {
      id: 'n3',
      title: 'Energy-chain commentary placeholder for OGDC and peers',
      summary:
        'Illustrative news explaining how oil-price moves may feed through.',
      source: 'Prototype sector note',
      publishedAt: '2024-10-13T07:50:00Z',
      importance: 'medium',
    },
    {
      id: 'n4',
      title: 'Learning-oriented note on how to read PSXviewAI research views',
      summary:
        'Onboarding example connecting headlines to evidence-based research.',
      source: 'PSXviewAI academy (fixture)',
      publishedAt: '2024-10-10T12:00:00Z',
      importance: 'low',
    },
  ],
};

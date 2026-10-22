import type { SourceRecord, SourceType } from '../types'

// Offline fallback sources. Live pipeline items replace these when /api/market
// responds; those records carry the exact article URL collected by the pipeline.
export const SOURCES: SourceRecord[] = [
  {
    confidence: 86,
    sources: [{
      title: 'OGDC announcements on PSX',
      type: 'Official',
      time: 'Official company record',
      text: 'Open the PSX company page to review OGDC announcements, financial results and payout records.',
      url: 'https://dps.psx.com.pk/company/OGDC',
    }],
  },
  {
    confidence: 72,
    sources: [{
      title: 'PPL announcements on PSX',
      type: 'Official',
      time: 'Official company record',
      text: 'Open the PSX company page to review PPL filings and regulatory announcements.',
      url: 'https://dps.psx.com.pk/company/PPL',
    }],
  },
  {
    confidence: 78,
    sources: [{
      title: 'State Bank monetary policy statements',
      type: 'Official',
      time: 'Official central-bank record',
      text: 'Review the original monetary policy statements and supporting documents from the State Bank of Pakistan.',
      url: 'https://www.sbp.org.pk/our-operations/publications/monetary-policy-statements/501',
    }],
  },
  {
    confidence: 81,
    sources: [{
      title: 'ENGRO announcements on PSX',
      type: 'Official',
      time: 'Official company record',
      text: 'Open the PSX company page to review ENGRO announcements and operational updates.',
      url: 'https://dps.psx.com.pk/company/ENGRO',
    }],
  },
  {
    confidence: 68,
    sources: [{
      title: 'LUCK announcements on PSX',
      type: 'Official',
      time: 'Official company record',
      text: 'Open the PSX company page to review Lucky Cement announcements, reports and financial results.',
      url: 'https://dps.psx.com.pk/company/LUCK',
    }],
  },
  {
    confidence: 84,
    sources: [{
      title: 'MARI announcements on PSX',
      type: 'Official',
      time: 'Official company record',
      text: 'Open the PSX company page to review Mari Energies announcements and production updates.',
      url: 'https://dps.psx.com.pk/company/MARI',
    }],
  },
  {
    confidence: 70,
    sources: [{
      title: 'NFDC fertilizer statistics',
      type: 'Data',
      time: 'Official industry data',
      text: 'Review fertilizer production, availability and offtake statistics from the National Fertilizer Development Centre.',
      url: 'https://nfdc.gov.pk/stat.html',
    }],
  },
]

export type { SourceType }

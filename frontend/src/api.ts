import type { Announcement, Company, SourceRecord } from './types'

export interface MarketData {
  companies: Company[]
  announcements: Announcement[]
  sources: SourceRecord[]
  asOf: string
}

// Fetch the full market bundle from the FastAPI backend. In dev the Vite
// proxy maps /api -> http://localhost:8000, so no CORS is needed there.
export async function fetchMarket(): Promise<MarketData> {
  const res = await fetch('/api/market')
  if (!res.ok) throw new Error(`market fetch failed: ${res.status}`)
  return (await res.json()) as MarketData
}

export async function fetchHealth(): Promise<boolean> {
  try {
    const res = await fetch('/api/health')
    return res.ok
  } catch {
    return false
  }
}

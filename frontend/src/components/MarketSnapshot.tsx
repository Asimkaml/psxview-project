import CompanyCard from './CompanyCard'
import { useData } from '../context/DataContext'

const RANGES: Array<[string, number]> = [
  ['1W', 7],
  ['1M', 30],
  ['3M', 90],
]

interface Props {
  range: number
  onRangeChange: (n: number) => void
  highlightSymbol: string | null
}

export default function MarketSnapshot({
  range,
  onRangeChange,
  highlightSymbol,
}: Props) {
  const { companies, asOf, loading, apiOnline } = useData()
  return (
    <main>
      <h1>PSX's 7 major companies at a glance</h1>
      <p className="sub">
        Price and volume come from PSX data. Click a scrolling news item above
        to open its impact analysis.
      </p>
      <div className="stamp">
        <span>
          Market data: {asOf || '—'}{asOf ? ', close' : ''}
        </span>
        <span>{apiOnline ? 'Live PSX data' : 'Waiting for PSX data…'}</span>
      </div>
      <div className="ph">
        <h2>Market snapshot</h2>
        <div className="rng">
          {RANGES.map(([label, n]) => (
            <button
              key={label}
              aria-pressed={n === range}
              onClick={() => onRangeChange(n)}
            >
              {label}
            </button>
          ))}
        </div>
      </div>
      {loading ? (
        <p className="hint">Loading live PSX data…</p>
      ) : companies.length === 0 ? (
        <p className="hint">Unable to load live PSX data right now.</p>
      ) : (
        <div className="grid">
          {companies.map((c) => (
            <CompanyCard
              key={c.symbol}
              company={c}
              range={range}
              highlighted={highlightSymbol === c.symbol}
            />
          ))}
        </div>
      )}
      <p className="hint">
        Tip: hover over the graph to see each day's price.
      </p>
    </main>
  )
}

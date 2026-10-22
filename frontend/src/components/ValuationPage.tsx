import { useEffect, useMemo, useState } from 'react'
import { valuationApi, type SavedItem, type ValuationBody } from '../api'
import { useAuth } from '../context/AuthContext'
import { useData } from '../context/DataContext'
import { computeAll } from '../lib/dcf'
import ValuationChart from './ValuationChart'
import './valuation.css'

const SCENARIOS = {
  conservative: { label: 'Conservative', growth: 4, terminal: 2.5 },
  base: { label: 'Base case', growth: 8, terminal: 3.5 },
  optimistic: { label: 'Optimistic', growth: 15, terminal: 4 },
} as const

type Scenario = keyof typeof SCENARIOS

function Slider(p: {
  label: string
  value: number
  min: number
  max: number
  step: number
  suffix: string
  onChange: (v: number) => void
}) {
  return (
    <div className="v-slider">
      <div className="v-row">
        <span>{p.label}</span>
        <b>
          {p.value.toFixed(p.step < 1 ? 1 : 0)}
          {p.suffix}
        </b>
      </div>
      <input
        type="range"
        min={p.min}
        max={p.max}
        step={p.step}
        value={p.value}
        onChange={(e) => p.onChange(parseFloat(e.target.value))}
        aria-label={p.label}
      />
    </div>
  )
}

export default function ValuationPage({ onNeedLogin }: { onNeedLogin: () => void }) {
  const { companies } = useData()
  const { user, checking } = useAuth()

  const [symbol, setSymbol] = useState('')
  const [eps, setEps] = useState('')
  const [price, setPrice] = useState('')
  const [advanced, setAdvanced] = useState(false)
  const [scenario, setScenario] = useState<Scenario | 'custom'>('base')
  const [rf, setRf] = useState(11)
  const [erp, setErp] = useState(6)
  const [beta, setBeta] = useState(1)
  const [years, setYears] = useState(5)
  const [growth, setGrowth] = useState(8)
  const [terminal, setTerminal] = useState(3.5)

  const [saved, setSaved] = useState<SavedItem[]>([])
  const [aiText, setAiText] = useState('')
  const [aiSource, setAiSource] = useState('')
  const [note, setNote] = useState('')
  const [busy, setBusy] = useState(false)

  const selectedCompany = companies.find((company) => company.symbol === symbol)
  const usesPsxEps = Boolean(selectedCompany && selectedCompany.eps > 0)

  // Selecting a PSX company fills its live price and extracted EPS. Manual
  // entry remains available through Custom or when the package has no EPS.
  function pickCompany(sym: string) {
    setSymbol(sym)
    const company = companies.find((item) => item.symbol === sym)
    if (company) {
      setPrice(String(company.price))
      setEps(company.eps > 0 ? String(company.eps) : '')
    } else {
      setPrice('')
      setEps('')
    }
    setAiText('')
  }

  function chooseScenario(next: Scenario) {
    const values = SCENARIOS[next]
    setScenario(next)
    setGrowth(values.growth)
    setTerminal(values.terminal)
    setAiText('')
  }

  function useSimpleMode() {
    setAdvanced(false)
    setRf(11)
    setErp(6)
    setBeta(1)
    setYears(5)
  }

  const calc = useMemo(() => {
    const e = parseFloat(eps)
    const p = parseFloat(price)
    if (!(e > 0 && p > 0)) {
      return { ok: false as const, msg: 'Select a company with EPS data, or enter custom values.' }
    }
    try {
      return {
        ok: true as const,
        res: computeAll({
          eps: e,
          price: p,
          rfPct: rf,
          erpPct: erp,
          beta,
          years,
          growthPct: growth,
          terminalPct: terminal,
        }),
      }
    } catch (err) {
      return { ok: false as const, msg: (err as Error).message }
    }
  }, [eps, price, rf, erp, beta, years, growth, terminal])

  const body = (): ValuationBody => ({
    symbol: symbol || 'CUSTOM',
    eps: parseFloat(eps),
    price: parseFloat(price),
    rf_pct: rf,
    erp_pct: erp,
    beta,
    years,
    growth_pct: growth,
    terminal_pct: terminal,
  })

  const loadSaved = () => valuationApi.list().then(setSaved).catch(() => setSaved([]))
  useEffect(() => {
    if (user) void loadSaved()
    else setSaved([])
  }, [user])

  async function run(fn: () => Promise<void>) {
    setBusy(true)
    setNote('')
    try {
      await fn()
    } catch (e) {
      setNote((e as Error).message)
    } finally {
      setBusy(false)
    }
  }

  if (checking) return <main className="vwrap"><p>Loading…</p></main>
  if (!user) {
    return (
      <main className="vwrap">
        <div className="v-card v-center">
          <h2>Valuation tool</h2>
          <p>Log in to use the reverse-DCF valuation tool and save your work.</p>
          <button className="vbtn" onClick={onNeedLogin}>Login / Sign up</button>
        </div>
      </main>
    )
  }

  const res = calc.ok ? calc.res : null
  const verdict = !res
    ? null
    : res.upsidePct >= 15
      ? { label: 'Potentially undervalued', tone: 'up' }
      : res.upsidePct <= -15
        ? { label: 'Potentially overvalued', tone: 'down' }
        : { label: 'Close to fair value', tone: 'neutral' }

  return (
    <main className="vwrap">
      <div className="v-title-row">
        <div>
          <h1>Reverse DCF valuation</h1>
          <p className="v-sub">Select a company, choose a scenario, and see the result instantly.</p>
        </div>
        <div className="v-mode" role="group" aria-label="Valuation complexity">
          <button className={!advanced ? 'on' : ''} onClick={useSimpleMode}>Simple</button>
          <button className={advanced ? 'on' : ''} onClick={() => setAdvanced(true)}>Advanced</button>
        </div>
      </div>

      <section className="v-card">
        <h3>1. Select a company</h3>
        <div className="v-grid3">
          <label>Company
            <select value={symbol} onChange={(e) => pickCompany(e.target.value)}>
              <option value="">Custom values…</option>
              {companies.map((company) => (
                <option key={company.symbol} value={company.symbol}>
                  {company.symbol}{company.eps > 0 ? '' : ' (EPS unavailable)'}
                </option>
              ))}
            </select>
          </label>
          <label>EPS (Rs)
            <input
              type="number"
              min="0"
              step="0.01"
              value={eps}
              readOnly={usesPsxEps}
              onChange={(e) => setEps(e.target.value)}
            />
            {usesPsxEps && <small className="v-source">From PSX market data</small>}
          </label>
          <label>Current price (Rs)
            <input
              type="number"
              min="0"
              step="0.01"
              value={price}
              readOnly={Boolean(selectedCompany)}
              onChange={(e) => setPrice(e.target.value)}
            />
            {selectedCompany && <small className="v-source">From PSX market data</small>}
          </label>
        </div>
      </section>

      <section className="v-card">
        <h3>2. Choose your outlook</h3>
        <div className="v-scenarios" role="group" aria-label="Growth scenario">
          {(Object.keys(SCENARIOS) as Scenario[]).map((key) => (
            <button
              key={key}
              className={scenario === key ? 'on' : ''}
              aria-pressed={scenario === key}
              onClick={() => chooseScenario(key)}
            >
              <b>{SCENARIOS[key].label}</b>
              <span>{SCENARIOS[key].growth}% growth</span>
            </button>
          ))}
        </div>
        <Slider
          label="Expected annual earnings growth"
          value={growth}
          min={0}
          max={100}
          step={0.5}
          suffix="%"
          onChange={(value) => {
            setGrowth(value)
            setScenario('custom')
          }}
        />
        {!advanced && (
          <p className="v-assumption-note">
            Using standard assumptions: 11% government bond return, 6% additional stock-market return,
            average share-price risk, and a 5-year forecast.
          </p>
        )}
      </section>

      {advanced && (
        <section className="v-card">
          <h3>Advanced assumptions</h3>
          <div className="v-grid2">
            <Slider label="Government bond return" value={rf} min={5} max={22} step={0.5} suffix="%" onChange={setRf} />
            <Slider label="Extra return expected from stocks" value={erp} min={2} max={14} step={0.5} suffix="%" onChange={setErp} />
            <Slider label="Share-price risk (beta)" value={beta} min={0.3} max={2.5} step={0.1} suffix="×" onChange={setBeta} />
            <Slider label="Long-term growth" value={terminal} min={0} max={8} step={0.5} suffix="%" onChange={setTerminal} />
          </div>
          <p className="v-field-title">Forecast period</p>
          <div className="v-years">
            {[3, 5, 10].map((year) => (
              <button key={year} className={year === years ? 'on' : ''} onClick={() => setYears(year)}>
                {year} years
              </button>
            ))}
          </div>
        </section>
      )}

      {!res ? (
        <p className="v-warn">{calc.ok ? '' : calc.msg}</p>
      ) : (
        <>
          <section className="v-card v-results">
            <div className="v-big">
              <small>Estimated fair value</small>
              <strong>Rs {res.fairValue.toFixed(0)}</strong>
              <span className={`v-verdict ${verdict?.tone ?? 'neutral'}`}>{verdict?.label}</span>
              <small className={res.upsidePct >= 0 ? 'up' : 'down'}>
                {res.upsidePct >= 0 ? '+' : ''}{res.upsidePct.toFixed(0)}% versus current price
              </small>
            </div>
            <div className="v-big">
              <small>Growth expected by the current price</small>
              <strong>{res.impliedGrowthPct === null ? '>500%' : `${res.impliedGrowthPct.toFixed(1)}%`}</strong>
              <small>per year · required return {res.requiredReturnPct.toFixed(1)}%</small>
            </div>
          </section>

          <section className="v-card">
            <h3>How the result changes at other growth rates</h3>
            <ValuationChart
              growthAxis={res.growthAxis}
              upsideCurve={res.upsideCurve}
              impliedGrowthPct={res.impliedGrowthPct}
            />
          </section>

          <section className="v-card">
            <div className="v-actions">
              <button className="vbtn" disabled={busy} onClick={() => run(async () => {
                await valuationApi.save(body())
                await loadSaved()
                setNote('Saved.')
              })}>Save valuation</button>
              <button className="vbtn alt" disabled={busy} onClick={() => run(async () => {
                const result = await valuationApi.explain(body())
                setAiText(result.text)
                setAiSource(result.source)
              })}>Explain with AI</button>
            </div>
            {note && <p className="v-note">{note}</p>}
            {aiText && (
              <div className="v-ai">
                <p>{aiText}</p>
                <small>{aiSource === 'gemini' ? 'Written by AI' : 'Basic summary (AI unavailable)'}</small>
              </div>
            )}
          </section>
        </>
      )}

      <section className="v-card">
        <h3>Saved valuations</h3>
        {saved.length === 0 ? <p className="v-sub">Nothing saved yet.</p> : (
          <ul className="v-saved">
            {saved.map((item) => (
              <li key={item.id}>
                <b>{item.symbol}</b>
                <span>
                  fair Rs {item.result.fair_value.toFixed(0)} · implied{' '}
                  {item.result.implied_growth_pct === null ? '>500' : item.result.implied_growth_pct.toFixed(1)}%
                </span>
                <button className="linkbtn" onClick={() => run(async () => {
                  await valuationApi.remove(item.id)
                  await loadSaved()
                })}>Delete</button>
              </li>
            ))}
          </ul>
        )}
      </section>

      <p className="v-disc">
        Educational tool only. Not a buy or sell recommendation. EPS is used as a cash-flow proxy.
        Not designed for banks or insurers.
      </p>
    </main>
  )
}

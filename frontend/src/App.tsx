import { useCallback, useEffect, useRef, useState } from 'react'
import Header from './components/Header'
import LoginPage from './components/LoginPage'
import MarketSnapshot from './components/MarketSnapshot'
import ValuationPage from './components/ValuationPage'
import SourcesModal from './components/SourcesModal'
import { DataProvider, useData } from './context/DataContext'
import { AuthProvider, useAuth } from './context/AuthContext'

function AppContent() {
  const { announcements } = useData()
  const { user, logout } = useAuth()
  const [active, setActive] = useState<number | null>(null)
  const [range, setRange] = useState(30)
  const [sourcesIndex, setSourcesIndex] = useState<number | null>(null)
  const [view, setView] = useState<'market' | 'valuation'>('market')

  const announcement = active !== null ? announcements[active] ?? null : null
  const highlightSymbol = announcement?.symbol ?? null
  const tickerPaused = active !== null

  const toggleAnnouncement = useCallback((index: number) => {
    setActive((prev) => (prev === index ? null : index))
  }, [])

  // Keep the latest open-layer state in refs so the Escape handler (added
  // once on mount) can decide which layer to close without stale closures.
  const sourcesRef = useRef(sourcesIndex)
  sourcesRef.current = sourcesIndex

  // Click outside the header and modals closes the announcement detail.
  useEffect(() => {
    const onDocClick = (e: MouseEvent) => {
      const t = e.target as HTMLElement | null
      if (!t) return
      if (!t.closest('#hdr, #smodal')) setActive(null)
    }
    document.addEventListener('click', onDocClick)
    return () => document.removeEventListener('click', onDocClick)
  }, [])

  // Escape closes the topmost open layer: sources -> announcement detail.
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key !== 'Escape') return
      if (sourcesRef.current !== null) {
        setSourcesIndex(null)
        return
      }
      setActive(null)
    }
    document.addEventListener('keydown', onKey)
    return () => document.removeEventListener('keydown', onKey)
  }, [])

  return (
    <>
      <Header
        announcement={announcement}
        active={active}
        tickerPaused={tickerPaused}
        onTickerItemClick={toggleAnnouncement}
        onValuationClick={() => {
          setActive(null)
          setView('valuation')
        }}
        onAnnouncementsClick={() => {
          setView('market')
          window.scrollTo({ top: 0 })
          setActive(0)
        }}
        userName={user?.name ?? ''}
        onLogout={() => void logout()}
        onCloseAnnouncement={() => setActive(null)}
        onViewSources={() => {
          if (active !== null) setSourcesIndex(active)
        }}
      />

      {view === 'market' ? (
        <MarketSnapshot
          range={range}
          onRangeChange={setRange}
          highlightSymbol={highlightSymbol}
        />
      ) : (
        <ValuationPage onNeedLogin={() => undefined} />
      )}

      {sourcesIndex !== null && (
        <SourcesModal
          index={sourcesIndex}
          onClose={() => setSourcesIndex(null)}
        />
      )}
    </>
  )
}

function AuthenticatedApp() {
  const { user, checking } = useAuth()

  if (checking) {
    return (
      <main className="auth-loading" aria-live="polite">
        <div className="auth-brand">PSXview<span>AI</span></div>
        <p>Checking your session…</p>
      </main>
    )
  }

  if (!user) return <LoginPage />

  return (
    <DataProvider>
      <AppContent />
    </DataProvider>
  )
}

export default function App() {
  return (
    <AuthProvider>
      <AuthenticatedApp />
    </AuthProvider>
  )
}

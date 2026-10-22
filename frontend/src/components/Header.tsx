import type { Announcement } from '../types'
import AnnouncementDetail from './AnnouncementDetail'
import Ticker from './Ticker'

interface Props {
  announcement: Announcement | null
  active: number | null
  tickerPaused: boolean
  onTickerItemClick: (index: number) => void
  onValuationClick: () => void
  onAnnouncementsClick: () => void
  userName: string
  onLogout: () => void
  onCloseAnnouncement: () => void
  onViewSources: () => void
}

export default function Header(props: Props) {
  return (
    <header id="hdr">
      <div className="bar">
        <div className="logo">
          PSXview<span>AI</span>
        </div>
        <button className="btn ghost" onClick={props.onValuationClick}>
          Valuation
        </button>
        <button className="btn ghost" onClick={props.onAnnouncementsClick}>
          Announcements
        </button>
        <span className="who">{props.userName}</span>
        <button className="btn ghost" onClick={props.onLogout}>
          Logout
        </button>
      </div>
      <Ticker
        paused={props.tickerPaused}
        active={props.active}
        onItemClick={props.onTickerItemClick}
      />
      <AnnouncementDetail
        announcement={props.announcement}
        onClose={props.onCloseAnnouncement}
        onViewSources={props.onViewSources}
      />
    </header>
  )
}

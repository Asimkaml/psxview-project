import { useData } from '../context/DataContext'

interface Props {
  index: number
  onClose: () => void
}

const safeSourceUrl = (url?: string) =>
  url && /^https?:\/\//i.test(url) ? url : null

export default function SourcesModal({ index, onClose }: Props) {
  const { announcements, sources } = useData()
  const announcement = announcements[index]
  const sourceRecord = sources[index]

  if (!announcement || !sourceRecord) return null

  return (
    <div
      className="modal open"
      id="smodal"
      role="dialog"
      aria-modal="true"
      aria-labelledby="sources-title"
      onClick={(event) => {
        if (event.target === event.currentTarget) onClose()
      }}
    >
      <div className="scard" id="sbody">
        <div className="sh">
          <div>
            <small>Original reporting and official references</small>
            <h3 id="sources-title">{announcement.headline}</h3>
          </div>
          <button className="x" aria-label="Close" onClick={onClose}>
            ×
          </button>
        </div>

        <div className="source-list">
          <p className="note">
            Open a source to read the original page in a new browser tab.
          </p>

          {sourceRecord.sources.length === 0 ? (
            <p className="source-empty">No source links are available for this announcement.</p>
          ) : (
            sourceRecord.sources.map((source, sourceIndex) => {
              const url = safeSourceUrl(source.url)
              return (
                <article className="source-item" key={`${source.title}-${sourceIndex}`}>
                  <div className="source-item-head">
                    <span className={`ty t-${source.type}`}>{source.type}</span>
                    <small>{source.time}</small>
                  </div>
                  <h4>{source.title}</h4>
                  <p>{source.text}</p>
                  {url ? (
                    <a href={url} target="_blank" rel="noopener noreferrer" className="source-link">
                      Open original source <span aria-hidden="true">↗</span>
                    </a>
                  ) : (
                    <span className="source-unavailable">Original link unavailable</span>
                  )}
                </article>
              )
            })
          )}

          <p className="source-disclaimer">
            Source pages are provided by third parties and open outside PSXviewAI.
          </p>
        </div>
      </div>
    </div>
  )
}

import { useEffect, useRef, useState } from 'react'
import type { AccountTab } from '../types'

interface Props {
  open: boolean
  tab: AccountTab
  onClose: () => void
}

// Account modal: Login / Sign up tabs, then a 6-digit 2-factor OTP step,
// then a "Verified" confirmation step — mirroring the prototype flow.
export default function AccountModal({ open, tab, onClose }: Props) {
  const [step, setStep] = useState(1)
  const [curTab, setCurTab] = useState<AccountTab>(tab)
  const emailRef = useRef<HTMLInputElement>(null)
  const otpRefs = useRef<(HTMLInputElement | null)[]>([])

  // Reset to step 1 and the requested tab whenever the modal opens.
  useEffect(() => {
    if (open) {
      setStep(1)
      setCurTab(tab)
      // Focus the email field once the first step is painted.
      requestAnimationFrame(() => emailRef.current?.focus())
    }
  }, [open, tab])

  if (!open) return null

  const isSignup = curTab === 'signup'

  return (
    <div
      className="modal open"
      id="modal"
      role="dialog"
      aria-modal="true"
      aria-label="Account"
      onClick={(e) => {
        if (e.target === e.currentTarget) onClose()
      }}
    >
      <div className="card">
        {/* Step 1: credentials */}
        <div style={{ display: step === 1 ? '' : 'none' }}>
          <div className="tabs" role="tablist">
            <button
              role="tab"
              aria-selected={!isSignup}
              onClick={() => setCurTab('login')}
            >
              Login
            </button>
            <button
              role="tab"
              aria-selected={isSignup}
              onClick={() => setCurTab('signup')}
            >
              Sign up
            </button>
          </div>
          <div style={{ display: isSignup ? '' : 'none' }}>
            <label htmlFor="nm">Full name</label>
            <input id="nm" autoComplete="name" />
          </div>
          <label htmlFor="em">Email</label>
          <input
            id="em"
            type="email"
            autoComplete="email"
            placeholder="you@example.com"
            ref={emailRef}
          />
          <label htmlFor="pw">Password</label>
          <input
            id="pw"
            type="password"
            autoComplete={isSignup ? 'new-password' : 'current-password'}
          />
          <button
            className="btn prime"
            onClick={() => {
              setStep(2)
              requestAnimationFrame(() => otpRefs.current[0]?.focus())
            }}
          >
            {isSignup ? 'Create account' : 'Login'}
          </button>
        </div>

        {/* Step 2: 2-factor verification */}
        <div style={{ display: step === 2 ? '' : 'none' }}>
          <h2 style={{ margin: '0 0 4px', fontSize: 20 }}>2-factor verification</h2>
          <p className="hint">Enter the 6-digit code sent to your email.</p>
          <div className="otp">
            {Array.from({ length: 6 }).map((_, i) => (
              <input
                key={i}
                maxLength={1}
                inputMode="numeric"
                aria-label={`Digit ${i + 1}`}
                ref={(el) => {
                  otpRefs.current[i] = el
                }}
                onChange={(e) => {
                  if (e.target.value && otpRefs.current[i + 1]) {
                    otpRefs.current[i + 1]!.focus()
                  }
                }}
                onKeyDown={(e) => {
                  if (
                    e.key === 'Backspace' &&
                    !e.currentTarget.value &&
                    otpRefs.current[i - 1]
                  ) {
                    otpRefs.current[i - 1]!.focus()
                  }
                }}
              />
            ))}
          </div>
          <button className="btn prime" onClick={() => setStep(3)}>
            Verify
          </button>
        </div>

        {/* Step 3: verified */}
        <div style={{ display: step === 3 ? '' : 'none', textAlign: 'center' }}>
          <h2 style={{ margin: '0 0 4px', fontSize: 20 }}>Verified</h2>
          <p className="hint">The user dashboard will open from here.</p>
          <button className="btn prime" onClick={onClose}>
            Close
          </button>
        </div>
      </div>
    </div>
  )
}

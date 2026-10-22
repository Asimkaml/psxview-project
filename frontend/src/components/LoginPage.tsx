import { useEffect, useRef, useState } from 'react'
import { authApi } from '../api'
import { useAuth } from '../context/AuthContext'
import type { AccountTab } from '../types'

export default function LoginPage() {
  const { setUser } = useAuth()
  const [tab, setTab] = useState<AccountTab>('login')
  const [step, setStep] = useState<'credentials' | 'otp'>('credentials')
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [challenge, setChallenge] = useState('')
  const [error, setError] = useState('')
  const [notice, setNotice] = useState('')
  const [busy, setBusy] = useState(false)
  const emailRef = useRef<HTMLInputElement>(null)
  const otpRefs = useRef<(HTMLInputElement | null)[]>([])

  const isSignup = tab === 'signup'

  useEffect(() => {
    emailRef.current?.focus()
  }, [])

  function switchTab(next: AccountTab) {
    setTab(next)
    setStep('credentials')
    setError('')
    setNotice('')
    setPassword('')
  }

  async function submitCredentials() {
    setError('')
    setNotice('')
    setBusy(true)
    try {
      const result = isSignup
        ? await authApi.register(name, email, password)
        : await authApi.login(email, password)
      setChallenge(result.challenge_token)
      setStep('otp')
      requestAnimationFrame(() => otpRefs.current[0]?.focus())
    } catch (err) {
      setError((err as Error).message)
    } finally {
      setBusy(false)
    }
  }

  async function submitCode() {
    const code = otpRefs.current.map((input) => input?.value ?? '').join('')
    if (code.length !== 6) {
      setError('Enter all 6 digits')
      return
    }

    setError('')
    setNotice('')
    setBusy(true)
    try {
      const user = await authApi.verifyOtp(challenge, code)
      setUser(user)
    } catch (err) {
      setError((err as Error).message)
    } finally {
      setBusy(false)
    }
  }

  async function resendCode() {
    setError('')
    setNotice('')
    setBusy(true)
    try {
      const result = await authApi.resendOtp(challenge)
      setChallenge(result.challenge_token)
      otpRefs.current.forEach((input) => {
        if (input) input.value = ''
      })
      setNotice('A new verification code was sent.')
      requestAnimationFrame(() => otpRefs.current[0]?.focus())
    } catch (err) {
      setError((err as Error).message)
    } finally {
      setBusy(false)
    }
  }

  return (
    <main className="auth-page">
      <section className="auth-intro" aria-label="About PSXviewAI">
        <div className="auth-brand">
          PSXview<span>AI</span>
        </div>
        <p className="auth-kicker">Pakistan Stock Exchange intelligence</p>
        <h1>Research the market with evidence, not noise.</h1>
        <p className="auth-copy">
          Follow market movement, review company announcements, and explore
          valuations from one focused dashboard.
        </p>
      </section>

      <section className="auth-panel" aria-labelledby="auth-title">
        <div className="auth-card">
          {step === 'credentials' ? (
            <form
              onSubmit={(event) => {
                event.preventDefault()
                void submitCredentials()
              }}
            >
              <div className="tabs" role="tablist" aria-label="Account action">
                <button
                  type="button"
                  role="tab"
                  aria-selected={!isSignup}
                  onClick={() => switchTab('login')}
                >
                  Login
                </button>
                <button
                  type="button"
                  role="tab"
                  aria-selected={isSignup}
                  onClick={() => switchTab('signup')}
                >
                  Sign up
                </button>
              </div>

              <h2 id="auth-title">{isSignup ? 'Create your account' : 'Welcome back'}</h2>
              <p className="auth-subtitle">
                {isSignup
                  ? 'Start with your details, then verify your email.'
                  : 'Sign in to open your market dashboard.'}
              </p>

              {isSignup && (
                <>
                  <label htmlFor="auth-name">Full name</label>
                  <input
                    id="auth-name"
                    autoComplete="name"
                    value={name}
                    onChange={(event) => setName(event.target.value)}
                    required
                  />
                </>
              )}

              <label htmlFor="auth-email">Email</label>
              <input
                id="auth-email"
                ref={emailRef}
                type="email"
                autoComplete="email"
                placeholder="you@example.com"
                value={email}
                onChange={(event) => setEmail(event.target.value)}
                required
              />

              <label htmlFor="auth-password">Password</label>
              <input
                id="auth-password"
                type="password"
                autoComplete={isSignup ? 'new-password' : 'current-password'}
                minLength={isSignup ? 8 : 1}
                maxLength={72}
                value={password}
                onChange={(event) => setPassword(event.target.value)}
                required
              />

              {error && <p className="auth-message error" role="alert">{error}</p>}

              <button className="auth-submit" type="submit" disabled={busy}>
                {busy ? 'Please wait…' : isSignup ? 'Create account' : 'Login'}
              </button>
            </form>
          ) : (
            <div>
              <button
                type="button"
                className="auth-back"
                onClick={() => {
                  setStep('credentials')
                  setError('')
                  setNotice('')
                }}
              >
                ← Back
              </button>
              <p className="auth-kicker">Two-factor verification</p>
              <h2 id="auth-title">Check your email</h2>
              <p className="auth-subtitle">
                Enter the six-digit code sent to <strong>{email}</strong>.
              </p>

              <div className="otp auth-otp">
                {Array.from({ length: 6 }).map((_, index) => (
                  <input
                    key={index}
                    maxLength={1}
                    inputMode="numeric"
                    pattern="[0-9]*"
                    aria-label={`Digit ${index + 1}`}
                    ref={(element) => {
                      otpRefs.current[index] = element
                    }}
                    onChange={(event) => {
                      event.currentTarget.value = event.currentTarget.value.replace(/\D/g, '')
                      if (event.currentTarget.value && otpRefs.current[index + 1]) {
                        otpRefs.current[index + 1]?.focus()
                      }
                    }}
                    onKeyDown={(event) => {
                      if (event.key === 'Backspace' && !event.currentTarget.value) {
                        otpRefs.current[index - 1]?.focus()
                      }
                      if (event.key === 'Enter') void submitCode()
                    }}
                  />
                ))}
              </div>

              {error && <p className="auth-message error" role="alert">{error}</p>}
              {notice && <p className="auth-message success" role="status">{notice}</p>}

              <button className="auth-submit" type="button" onClick={() => void submitCode()} disabled={busy}>
                {busy ? 'Checking…' : 'Verify and continue'}
              </button>
              <button className="auth-resend" type="button" onClick={() => void resendCode()} disabled={busy}>
                Send a new code
              </button>
            </div>
          )}
        </div>
      </section>
    </main>
  )
}

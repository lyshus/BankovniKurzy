import { useEffect, useState, useCallback } from 'react'
import { api } from './api/client'
import { CurrencySelector } from './components/CurrencySelector'
import { RatesTable } from './components/RatesTable'
import type { Currency, RateEntry, TradeMode } from './types'

const REFRESH_INTERVAL_MS = 5 * 60 * 1000  // 5 minut

export default function App() {
  const [currencies, setCurrencies] = useState<Currency[]>([])
  const [selected, setSelected] = useState('EUR')
  const [mode, setMode] = useState<TradeMode>('buy')
  const [rates, setRates] = useState<RateEntry[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [lastRefresh, setLastRefresh] = useState<Date | null>(null)

  // Načti seznam měn jednou při startu
  useEffect(() => {
    api.currencies()
      .then(setCurrencies)
      .catch(() => { /* tiché selhání — seznam měn není kritický */ })
  }, [])

  // Načti kurzy pro vybranou měnu
  const fetchRates = useCallback(() => {
    setLoading(true)
    setError(null)
    api.rates(selected)
      .then(data => {
        setRates(data)
        setLastRefresh(new Date())
      })
      .catch(err => {
        setError(`Nepodařilo se načíst kurzy: ${err.message}`)
      })
      .finally(() => setLoading(false))
  }, [selected])

  useEffect(() => {
    fetchRates()
    const interval = setInterval(fetchRates, REFRESH_INTERVAL_MS)
    return () => clearInterval(interval)
  }, [fetchRates])

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="border-b border-gray-200 bg-white shadow-sm">
        <div className="mx-auto max-w-5xl px-4 py-4">
          <div className="flex items-baseline justify-between">
            <div>
              <h1 className="text-xl font-bold text-gray-900">Bankovní kurzy</h1>
              <p className="text-xs text-gray-400 mt-0.5">kurzy.frapa.eu</p>
            </div>
            <div className="text-xs text-gray-400">
              {lastRefresh && (
                <>
                  Načteno {lastRefresh.toLocaleTimeString('cs-CZ', { hour: '2-digit', minute: '2-digit' })}
                  {' · '}
                </>
              )}
              <button
                onClick={fetchRates}
                className="text-blue-600 hover:underline"
                disabled={loading}
              >
                Obnovit
              </button>
            </div>
          </div>
        </div>
      </header>

      <main className="mx-auto max-w-5xl px-4 py-6 space-y-4">
        <CurrencySelector
          currencies={currencies}
          selected={selected}
          mode={mode}
          onCurrencyChange={setSelected}
          onModeChange={setMode}
        />

        <RatesTable
          rates={rates}
          currency={selected}
          mode={mode}
          loading={loading}
          error={error}
        />
      </main>

      <footer className="mt-8 border-t border-gray-200 bg-white py-4">
        <p className="text-center text-xs text-gray-400">
          Data jsou aktualizována automaticky z veřejných zdrojů bank. Kurzy jsou informativní.
        </p>
      </footer>
    </div>
  )
}

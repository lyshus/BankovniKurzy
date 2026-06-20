import type { RateEntry, TradeMode } from '../types'

interface Props {
  rates: RateEntry[]
  currency: string
  mode: TradeMode
  loading: boolean
  error: string | null
}

function formatRate(value: string | null, amount: number): string {
  if (value === null) return '–'
  const num = parseFloat(value)
  // Přepočítej na 1 jednotku (ČNB uvádí např. 100 HUF = X CZK)
  const perUnit = num / amount
  return perUnit.toFixed(3).replace('.', ',')
}

function formatDateTime(iso: string): string {
  return new Date(iso).toLocaleString('cs-CZ', {
    day: '2-digit',
    month: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  })
}

function formatNextUpdate(iso: string | null): string {
  if (!iso) return '–'
  const d = new Date(iso)
  const now = new Date()
  const diffMs = d.getTime() - now.getTime()
  if (diffMs < 0) return 'brzy'
  const hours = Math.floor(diffMs / 3_600_000)
  const minutes = Math.floor((diffMs % 3_600_000) / 60_000)
  if (hours > 0) return `za ${hours} h ${minutes} min`
  return `za ${minutes} min`
}

function sortRates(rates: RateEntry[], mode: TradeMode): RateEntry[] {
  return [...rates].sort((a, b) => {
    // Pokud chci KOUPIT → hledám nejlevnější sell rate (menší = lepší)
    // Pokud chci PRODAT → hledám nejdražší buy rate (větší = lepší)
    const aVal = mode === 'buy' ? a.rate_sell : a.rate_buy
    const bVal = mode === 'buy' ? b.rate_sell : b.rate_buy
    if (aVal === null && bVal === null) return 0
    if (aVal === null) return 1
    if (bVal === null) return -1
    const aNum = parseFloat(aVal) / a.amount
    const bNum = parseFloat(bVal) / b.amount
    return mode === 'buy' ? aNum - bNum : bNum - aNum
  })
}

export function RatesTable({ rates, currency, mode, loading, error }: Props) {
  if (loading) {
    return (
      <div className="flex items-center justify-center py-20 text-gray-400">
        <svg className="animate-spin h-6 w-6 mr-2" fill="none" viewBox="0 0 24 24">
          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z" />
        </svg>
        Načítám kurzy…
      </div>
    )
  }

  if (error) {
    return (
      <div className="rounded-lg bg-red-50 border border-red-200 p-4 text-red-700 text-sm">
        {error}
      </div>
    )
  }

  if (rates.length === 0) {
    return (
      <div className="text-center py-20 text-gray-400">
        Žádné kurzy pro {currency} nejsou zatím k dispozici.
      </div>
    )
  }

  const sorted = sortRates(rates, mode)
  const bestEntry = sorted[0]
  const bestVal = mode === 'buy' ? bestEntry?.rate_sell : bestEntry?.rate_buy

  return (
    <div className="overflow-x-auto rounded-xl border border-gray-200 bg-white shadow-sm">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-gray-100 bg-gray-50 text-left text-xs font-semibold uppercase tracking-wide text-gray-500">
            <th className="px-4 py-3">Banka</th>
            <th className="px-4 py-3 text-right">
              {mode === 'buy' ? '▼ Prodej (platím)' : '▲ Nákup (dostanu)'}
            </th>
            <th className="px-4 py-3 text-right text-gray-400">
              {mode === 'buy' ? 'Nákup' : 'Prodej'}
            </th>
            <th className="px-4 py-3 text-right text-gray-400">Střed (ČNB)</th>
            <th className="px-4 py-3 text-right">Platí od</th>
            <th className="px-4 py-3 text-right">Příští aktualizace</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-50">
          {sorted.map((entry, i) => {
            const primaryVal = mode === 'buy' ? entry.rate_sell : entry.rate_buy
            const secondaryVal = mode === 'buy' ? entry.rate_buy : entry.rate_sell
            const isBest = i === 0 && primaryVal !== null

            return (
              <tr
                key={entry.bank.code}
                className={`transition-colors hover:bg-blue-50 ${isBest ? 'bg-green-50' : ''}`}
              >
                <td className="px-4 py-3">
                  <a
                    href={entry.bank.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="font-medium text-blue-700 hover:underline"
                  >
                    {entry.bank.name}
                  </a>
                  {isBest && (
                    <span className="ml-2 rounded-full bg-green-100 px-2 py-0.5 text-xs font-semibold text-green-700">
                      nejlepší
                    </span>
                  )}
                </td>
                <td className="px-4 py-3 text-right tabular-nums">
                  <span className={`font-semibold ${isBest ? 'text-green-700' : 'text-gray-900'}`}>
                    {formatRate(primaryVal, entry.amount)} CZK
                  </span>
                </td>
                <td className="px-4 py-3 text-right tabular-nums text-gray-400">
                  {formatRate(secondaryVal, entry.amount)} CZK
                </td>
                <td className="px-4 py-3 text-right tabular-nums text-gray-400">
                  {formatRate(entry.rate_mid, entry.amount)} CZK
                </td>
                <td className="px-4 py-3 text-right text-gray-500">
                  {entry.valid_from}
                </td>
                <td className="px-4 py-3 text-right text-gray-400">
                  <span title={entry.next_update ? formatDateTime(entry.next_update) : undefined}>
                    {formatNextUpdate(entry.next_update)}
                  </span>
                </td>
              </tr>
            )
          })}
        </tbody>
      </table>
      <div className="border-t border-gray-100 px-4 py-2 text-xs text-gray-400">
        Kurzy jsou za 1 jednotku cizí měny v CZK.
        {bestVal && (
          <> Nejlepší {mode === 'buy' ? 'nákupní' : 'prodejní'} kurz: <strong>{formatRate(bestVal, bestEntry.amount)} CZK</strong> ({bestEntry.bank.name})</>
        )}
      </div>
    </div>
  )
}

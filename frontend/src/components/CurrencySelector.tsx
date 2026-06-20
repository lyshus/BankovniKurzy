import type { Currency, TradeMode } from '../types'

const PINNED = ['EUR', 'USD', 'GBP', 'CHF', 'PLN', 'HUF']

interface Props {
  currencies: Currency[]
  selected: string
  mode: TradeMode
  onCurrencyChange: (code: string) => void
  onModeChange: (mode: TradeMode) => void
}

export function CurrencySelector({ currencies, selected, mode, onCurrencyChange, onModeChange }: Props) {
  const pinned = PINNED.filter(c => currencies.some(x => x.code === c))
  const rest = currencies.filter(c => !PINNED.includes(c.code))

  return (
    <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
      {/* Rychlé tlačítka pro nejčastější měny */}
      <div className="flex flex-wrap gap-2">
        {pinned.map(code => (
          <button
            key={code}
            onClick={() => onCurrencyChange(code)}
            className={`px-4 py-2 rounded-lg font-medium text-sm transition-colors ${
              selected === code
                ? 'bg-blue-600 text-white shadow-sm'
                : 'bg-white text-gray-700 border border-gray-200 hover:bg-gray-50'
            }`}
          >
            {code}
          </button>
        ))}
        {/* Dropdown pro ostatní měny */}
        {rest.length > 0 && (
          <select
            value={pinned.includes(selected) ? '' : selected}
            onChange={e => e.target.value && onCurrencyChange(e.target.value)}
            className="px-3 py-2 rounded-lg border border-gray-200 bg-white text-sm text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="">Více měn…</option>
            {rest.map(c => (
              <option key={c.code} value={c.code}>
                {c.code} – {c.name_cz || c.name}
              </option>
            ))}
          </select>
        )}
      </div>

      {/* Přepínač: chci koupit / prodat */}
      <div className="flex rounded-lg border border-gray-200 bg-white overflow-hidden">
        <button
          onClick={() => onModeChange('buy')}
          className={`px-4 py-2 text-sm font-medium transition-colors ${
            mode === 'buy' ? 'bg-blue-600 text-white' : 'text-gray-600 hover:bg-gray-50'
          }`}
        >
          Chci koupit {selected}
        </button>
        <button
          onClick={() => onModeChange('sell')}
          className={`px-4 py-2 text-sm font-medium transition-colors border-l border-gray-200 ${
            mode === 'sell' ? 'bg-blue-600 text-white' : 'text-gray-600 hover:bg-gray-50'
          }`}
        >
          Chci prodat {selected}
        </button>
      </div>
    </div>
  )
}

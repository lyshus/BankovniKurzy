export interface Currency {
  code: string
  name: string
  name_cz: string
}

export interface Bank {
  code: string
  name: string
  url: string
}

export interface RateEntry {
  bank: Bank
  amount: number
  rate_buy: string | null   // Decimal jako string z DRF
  rate_sell: string | null
  rate_mid: string | null
  valid_from: string        // "2024-05-28"
  fetched_at: string        // ISO 8601
  next_update: string | null
}

// Uživatel chce buď KOUPIT cizí měnu (koukne na rate_sell)
// nebo PRODAT cizí měnu (koukne na rate_buy)
export type TradeMode = 'buy' | 'sell'

import type { Currency, RateEntry } from '../types'

const BASE = '/api/v1'

async function get<T>(path: string): Promise<T> {
  const res = await fetch(`${BASE}${path}`)
  if (!res.ok) throw new Error(`HTTP ${res.status}: ${path}`)
  return res.json() as Promise<T>
}

export const api = {
  currencies: (): Promise<Currency[]> => get('/currencies/'),
  rates: (currency: string): Promise<RateEntry[]> => get(`/rates/?currency=${currency}`),
}

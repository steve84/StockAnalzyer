import { Country } from './country';
import { Branch } from './branch';
import { Levermann } from './levermann';
import { StockIndex } from './stockindex';
import { IndexType } from './indextype';
import { Score } from './score';

export interface Stock {
  stockId?: number,
  nsin?: string,
  isin?: string,
  wkn?: string,
  symbol?: string,
  url?: string,
  businessYearEnd?: string,
  country?: Country,
  branch?: Branch,
  name?: string,
  levermann?: Levermann,
  scores?: Score[],
  stockCategory?: string,
  indices?: any[],
  stockIndex?: StockIndex[],
  indexParticipation?: any[],
  indexNames: string
}

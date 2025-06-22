// Use type safe message keys with `next-intl`
import type { Messages } from './types/translations';

declare global {
  // Use type safe message keys with `next-intl`
  interface IntlMessages extends Messages {}
}
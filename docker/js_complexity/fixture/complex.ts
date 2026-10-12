// A deliberately complex module: a reducer, a store, a scoring loop and a
// set of branchy rules. Used to check that FTA flags it.

export interface Item {
  id: string;
  price: number;
  quantity: number;
  tags?: string[];
  discount?: number;
}

export interface State {
  items: Item[];
  coupon: string | null;
  status: "idle" | "loading" | "ready" | "error";
  error?: string;
}

export type Action =
  | { type: "add"; item: Item }
  | { type: "remove"; id: string }
  | { type: "update"; id: string; quantity: number }
  | { type: "coupon"; code: string | null }
  | { type: "load" }
  | { type: "loaded"; items: Item[] }
  | { type: "fail"; error: string }
  | { type: "reset" };

export const initialState: State = { items: [], coupon: null, status: "idle" };

export function reducer(state: State, action: Action): State {
  switch (action.type) {
    case "add": {
      const existing = state.items.find((item) => item.id === action.item.id);
      if (existing) {
        return {
          ...state,
          items: state.items.map((item) =>
            item.id === action.item.id
              ? { ...item, quantity: item.quantity + action.item.quantity }
              : item,
          ),
        };
      }
      return { ...state, items: [...state.items, action.item] };
    }
    case "remove":
      return { ...state, items: state.items.filter((item) => item.id !== action.id) };
    case "update":
      if (action.quantity <= 0) {
        return { ...state, items: state.items.filter((item) => item.id !== action.id) };
      }
      return {
        ...state,
        items: state.items.map((item) =>
          item.id === action.id ? { ...item, quantity: action.quantity } : item,
        ),
      };
    case "coupon":
      return { ...state, coupon: action.code && action.code.trim() ? action.code.trim() : null };
    case "load":
      return state.status === "loading" ? state : { ...state, status: "loading" };
    case "loaded":
      return { ...state, items: action.items, status: "ready", error: undefined };
    case "fail":
      return { ...state, status: "error", error: action.error || "unknown error" };
    case "reset":
      return initialState;
    default:
      return state;
  }
}

export class Store<T extends State = State> {
  private state: T;
  private listeners: Array<(state: T) => void> = [];

  constructor(initial: T) {
    this.state = initial;
  }

  getState(): T {
    return this.state;
  }

  subscribe(listener: (state: T) => void): () => void {
    this.listeners.push(listener);
    return () => {
      this.listeners = this.listeners.filter((other) => other !== listener);
    };
  }

  dispatch(action: Action): void {
    try {
      const next = reducer(this.state, action) as T;
      if (next === this.state) {
        return;
      }
      this.state = next;
      this.notify();
    } catch (error) {
      const message = error instanceof Error ? error.message : String(error);
      this.state = { ...this.state, status: "error", error: message };
    }
  }

  private notify(): void {
    for (const listener of this.listeners) {
      try {
        listener(this.state);
      } catch (error) {
        if (error instanceof TypeError) {
          continue;
        }
        throw error;
      }
    }
  }

  restore(serialized: string | null): boolean {
    if (!serialized) {
      return false;
    }
    try {
      const parsed = JSON.parse(serialized) as Partial<T>;
      if (!parsed || !Array.isArray(parsed.items)) {
        return false;
      }
      this.state = { ...this.state, ...parsed };
      this.notify();
      return true;
    } catch {
      return false;
    } finally {
      this.listeners = [...this.listeners];
    }
  }
}

export type Rule = (item: Item, state: State) => number;

export function ruleBulk(item: Item): number {
  if (item.quantity >= 100) return 0.2;
  if (item.quantity >= 50) return 0.1;
  if (item.quantity >= 10) return 0.05;
  return 0;
}

export function ruleCoupon(_item: Item, state: State): number {
  if (!state.coupon) return 0;
  if (state.coupon === "HALF") return 0.5;
  if (state.coupon.startsWith("VIP")) return 0.15;
  return state.coupon.length > 8 ? 0.02 : 0.01;
}

export function ruleTags(item: Item): number {
  const tags = item.tags ?? [];
  if (tags.includes("clearance")) return 0.3;
  if (tags.includes("sale") && tags.includes("member")) return 0.12;
  if (tags.includes("sale") || tags.includes("promo")) return 0.08;
  return 0;
}

export function ruleExpensive(item: Item): number {
  if (item.price > 1000 && item.quantity > 1) return 0.07;
  if (item.price > 500) return 0.03;
  return 0;
}

export function ruleOwnDiscount(item: Item): number {
  const discount = item.discount ?? 0;
  if (discount < 0 || discount > 1) return 0;
  return discount > 0.5 ? 0.5 : discount;
}

export function ruleStatus(_item: Item, state: State): number {
  if (state.status === "error") return 0;
  if (state.status === "loading" || state.status === "idle") return 0;
  return state.items.length > 20 ? 0.02 : 0;
}

export function ruleOddId(item: Item): number {
  const last = item.id.charCodeAt(item.id.length - 1);
  if (Number.isNaN(last)) return 0;
  return last % 2 === 1 ? 0.01 : 0;
}

export function ruleMixedCart(_item: Item, state: State): number {
  const tagged = state.items.filter((other) => (other.tags ?? []).length > 0);
  if (tagged.length === 0) return 0;
  if (tagged.length === state.items.length) return 0.04;
  return tagged.length * 2 > state.items.length ? 0.02 : 0.01;
}

export function ruleSingle(item: Item, state: State): number {
  if (state.items.length !== 1) return 0;
  if (item.quantity === 1 && item.price < 10) return 0;
  return item.quantity > 1 ? 0.03 : 0.01;
}

export function ruleCheap(item: Item): number {
  if (item.price <= 0) return 0;
  if (item.price < 1 && item.quantity < 5) return -0.1;
  return item.price < 5 ? -0.02 : 0;
}

export function ruleWeekend(_item: Item, _state: State, day = new Date().getDay()): number {
  if (day === 0 || day === 6) return 0.05;
  if (day === 5) return 0.02;
  return 0;
}

export function ruleCap(item: Item, state: State): number {
  const count = state.items.reduce((sum, other) => sum + other.quantity, 0);
  if (count > 500 && item.quantity > 100) return -0.05;
  if (count > 200) return -0.01;
  return 0;
}

export const rules: Rule[] = [
  ruleBulk, ruleCoupon, ruleTags, ruleExpensive, ruleOwnDiscount, ruleStatus,
  ruleOddId, ruleMixedCart, ruleSingle, ruleCheap, ruleWeekend, ruleCap,
];

export function score(state: State, maxDiscount = 0.6): Map<string, number> {
  const scores = new Map<string, number>();
  for (const item of state.items) {
    let discount = 0;
    for (const rule of rules) {
      const value = rule(item, state);
      if (Number.isNaN(value)) {
        continue;
      } else if (value < 0 && discount + value < 0) {
        discount = 0;
      } else {
        discount += value;
      }
      if (discount >= maxDiscount) {
        discount = maxDiscount;
        break;
      }
    }
    const price = item.price * item.quantity * (1 - discount);
    scores.set(item.id, price > 0 ? Math.round(price * 100) / 100 : 0);
  }
  return scores;
}

export function total(state: State): number {
  let sum = 0;
  for (const value of score(state).values()) {
    sum += value;
  }
  return sum;
}

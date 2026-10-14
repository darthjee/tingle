// A plain TypeScript module whose name ends in ".vue.ts", next to Cart.vue.
// It must be analysed as its own file, separately from Cart.vue.
export interface CartLine { sku: string; quantity: number }

export function lineCount(lines: CartLine[]): number {
  return lines.reduce((total, line) => total + (line.quantity > 0 ? line.quantity : 0), 0);
}

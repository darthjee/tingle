<template>
  <div class="cart">
    <p>Total: {{ total }}</p>
  </div>
</template>

<script setup lang="ts">
import { computed } from "vue";

interface Item { price: number; quantity: number; discount?: number }
const props = defineProps<{ items: Item[] }>();

const total = computed(() => {
  let sum = 0;
  for (const item of props.items) {
    const discount = item.discount ?? 0;
    sum += item.price * item.quantity * (1 - discount);
  }
  return sum > 0 ? Math.round(sum * 100) / 100 : 0;
});
defineExpose({ total });
</script>

<style scoped>
.cart {
  padding: 1rem;
}
</style>

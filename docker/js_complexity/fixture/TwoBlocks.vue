<template>
  <ul>
    <li v-for="tag in visibleTags" :key="tag">{{ label(tag) }}</li>
  </ul>
</template>

<script>
export function normaliseTag(tag) {
  if (!tag) return "";
  return tag.trim().toLowerCase();
}
</script>

<script setup lang="ts">
const props = defineProps<{ tags: string[]; limit?: number }>();

function label(tag: string): string {
  return tag.length > 12 ? `${tag.slice(0, 12)}…` : tag;
}

const visibleTags = props.tags
  .map((tag) => normaliseTag(tag))
  .filter((tag) => tag !== "")
  .slice(0, props.limit ?? 5);
</script>

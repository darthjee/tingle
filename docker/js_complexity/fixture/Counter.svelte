<script context="module">
  let instances = 0;

  export function instanceCount() {
    return instances;
  }
</script>

<script lang="ts">
  export let start: number = 0;
  export let step: number = 1;

  let count = start;
  instances += 1;

  function increment(): void {
    count = count + step > 100 ? 100 : count + step;
  }
</script>

<button on:click={increment}>Count: {count}</button>

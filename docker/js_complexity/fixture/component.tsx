import { useEffect, useState } from "react";

interface CounterProps {
  start?: number;
  label: string;
}

export function Counter({ start = 0, label }: CounterProps) {
  const [count, setCount] = useState<number>(start);

  useEffect(() => {
    if (count > 10) {
      setCount(0);
    }
  }, [count]);

  const increment = () => setCount(count + 1);

  return (
    <button type="button" onClick={increment}>
      {label}: {count > 0 ? count : "none"}
    </button>
  );
}

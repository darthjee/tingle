export function Widget({ title, items, loading }) {
  const count = items ? items.length : 0;
  return (
    <section className="widget">
      <h2>{title}</h2>
      {loading ? <p>Loading...</p> : <p>{count} items</p>}
      <footer>{count === 0 && "Nothing here"}</footer>
    </section>
  );
}

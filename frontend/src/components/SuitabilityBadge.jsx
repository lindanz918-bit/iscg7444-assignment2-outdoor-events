function SuitabilityBadge({ score, advice }) {
  return (
    <div>
      <h3>Outdoor Suitability</h3>
      <p style={{ fontSize: "32px", fontWeight: "bold" }}>{score} / 100</p>
      <p>{advice}</p>
    </div>
  );
}

export default SuitabilityBadge;
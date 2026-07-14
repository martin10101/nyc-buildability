export default function HomePage() {
  return (
    <section style={{ padding: "3rem 1.5rem", maxWidth: "72ch" }}>
      <h1 style={{ fontSize: "1.75rem", marginBottom: "0.5rem" }}>
        NYC Buildability
      </h1>
      <p style={{ fontSize: "1rem", color: "#3d3d3d" }}>
        NYC Development Feasibility &amp; Zoning Intelligence Platform.
      </p>
      <p style={{ fontSize: "0.95rem", color: "#5a5a5a" }}>
        Milestone M0 placeholder. The Property / Confirm / Compare / Evidence
        experience will be implemented in later milestones on top of the
        canonical property-profile contract.
      </p>
    </section>
  );
}

// S4 scenario: deliberate lint failure (unused variable) - will be reverted
const s4DeliberateLintFailure = "unused";

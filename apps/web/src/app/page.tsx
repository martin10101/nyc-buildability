import Link from "next/link";

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
        Internal development build. The first slice of the Property / Confirm
        / Compare / Evidence experience is the BBL property lookup below;
        later milestones add the remaining stages on top of the canonical
        property-profile contract.
      </p>
      <p>
        <Link href="/property">Open the property lookup (BBL)</Link>
      </p>
    </section>
  );
}

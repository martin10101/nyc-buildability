import Link from "next/link";
import "./property/architect.css";

export default function HomePage() {
  return <div className="architect-shell"><header className="architect-topbar"><span className="architect-brand">NYC BUILDABILITY</span><span className="architect-environment">Internal development build</span></header><section className="architect-welcome"><p className="architect-eyebrow">Property intelligence · New York City</p><h1>From property facts<br />to an informed next step.</h1><p>Official records, preliminary development analysis and the evidence behind every result, in one workspace.</p><Link className="primary-button" href="/property">Open workspace →</Link><p className="section-note">Available tools follow the capabilities enabled in this environment. Preliminary results require professional review.</p></section></div>;
}

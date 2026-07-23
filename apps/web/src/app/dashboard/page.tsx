import type { Metadata } from 'next';
import { notFound } from 'next/navigation';
import { InternalBanner } from '@/components/property/InternalBanner';
import { DashboardApp } from '@/components/dashboard/DashboardApp';
import { dashboardEnabled } from '@/lib/dashboard/config';
import { getDashboardModel } from '@/lib/dashboard/server';
import './dashboard.css';

// Read the live ledger on every request (owner directive: near-real-time).
export const dynamic = 'force-dynamic';

export const metadata: Metadata = {
  title: 'Owner Mission Control — NYC Buildability (internal)',
};

/**
 * Read-only owner Mission-Control dashboard (task M0-T022).
 * INTERNAL ONLY: gated behind the non-public runtime flag
 * INTERNAL_OWNER_DASHBOARD_ENABLED (fail-safe off). When disabled the route
 * returns 404 (notFound) with no hint the feature exists — the app has no auth
 * yet, so this must never be exposed publicly. This is a Server Component: it
 * reads the flag and the control-plane files server-side and passes a plain
 * serializable model into the client tree. It performs no writes.
 */
export default async function DashboardPage() {
  if (!dashboardEnabled()) notFound();
  const model = await getDashboardModel();
  return (
    <div className="dash-shell">
      <InternalBanner />
      <DashboardApp model={model} />
    </div>
  );
}

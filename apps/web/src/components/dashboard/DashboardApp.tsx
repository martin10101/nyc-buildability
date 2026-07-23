'use client';

import { useRef, useState } from 'react';
import type { KeyboardEvent as ReactKeyboardEvent } from 'react';
import type { DashboardModel } from '@/lib/dashboard/types';
import { HealthDot } from './ui';
import { MissionControl } from './MissionControl';
import { ProductMap } from './ProductMap';
import { CurrentWork } from './CurrentWork';
import { Roadmap } from './Roadmap';
import { ActivityFeed } from './ActivityFeed';
import { SystemDrawer } from './SystemDrawer';

type View = 'mission' | 'map' | 'work' | 'roadmap' | 'activity';
const TABS: Array<{ id: View; label: string }> = [
  { id: 'mission', label: 'Mission Control' },
  { id: 'map', label: 'Product Map' },
  { id: 'work', label: 'Current Work' },
  { id: 'roadmap', label: 'Roadmap' },
  { id: 'activity', label: 'What Changed' },
];

export function DashboardApp({ model }: { model: DashboardModel }) {
  const [view, setView] = useState<View>('mission');
  const [selectedSystemId, setSelectedSystemId] = useState<string | null>(null);
  const [viewMode, setViewMode] = useState<'owner' | 'technical'>('owner');
  const tabRefs = useRef<Array<HTMLButtonElement | null>>([]);

  const selectedSystem = selectedSystemId
    ? model.systems.find((s) => s.id === selectedSystemId) ?? null
    : null;

  const onTabKey = (e: ReactKeyboardEvent, idx: number) => {
    if (e.key !== 'ArrowRight' && e.key !== 'ArrowLeft') return;
    e.preventDefault();
    const dir = e.key === 'ArrowRight' ? 1 : -1;
    const next = (idx + dir + TABS.length) % TABS.length;
    setView(TABS[next].id);
    tabRefs.current[next]?.focus();
  };

  return (
    <div className="dash-root">
      <header className="dash-header">
        <div className="dash-header-main">
          <h1 className="dash-h1">{model.project.name}</h1>
          <span className="dash-subtitle">Owner Mission Control · read-only</span>
        </div>
        <div className="dash-header-side">
          <span className="dash-overall-health">
            <HealthDot health={model.health.overall} showLabel />
          </span>
          <div className="dash-mode-toggle" role="group" aria-label="Detail level">
            <button type="button" aria-pressed={viewMode === 'owner'}
              className={viewMode === 'owner' ? 'dash-mode-on' : ''} onClick={() => setViewMode('owner')}>Owner</button>
            <button type="button" aria-pressed={viewMode === 'technical'}
              className={viewMode === 'technical' ? 'dash-mode-on' : ''} onClick={() => setViewMode('technical')}>Technical</button>
          </div>
        </div>
      </header>

      <div className="dash-tabs" role="tablist" aria-label="Dashboard views">
        {TABS.map((t, i) => (
          <button
            key={t.id}
            ref={(el) => { tabRefs.current[i] = el; }}
            role="tab"
            id={`dash-tab-${t.id}`}
            aria-selected={view === t.id}
            aria-controls={`dash-panel-${t.id}`}
            tabIndex={view === t.id ? 0 : -1}
            className={`dash-tab ${view === t.id ? 'dash-tab-active' : ''}`}
            onClick={() => setView(t.id)}
            onKeyDown={(e) => onTabKey(e, i)}
          >
            {t.label}
          </button>
        ))}
      </div>

      <div
        role="tabpanel"
        id={`dash-panel-${view}`}
        aria-labelledby={`dash-tab-${view}`}
        tabIndex={0}
        className="dash-panel"
      >
        {view === 'mission' && (
          <MissionControl model={model} onSelectSystem={setSelectedSystemId} onGoto={(v) => setView(v as View)} />
        )}
        {view === 'map' && <ProductMap model={model} onSelectSystem={setSelectedSystemId} />}
        {view === 'work' && <CurrentWork model={model} viewMode={viewMode} onSelectSystem={setSelectedSystemId} />}
        {view === 'roadmap' && <Roadmap model={model} viewMode={viewMode} onSelectSystem={setSelectedSystemId} />}
        {view === 'activity' && <ActivityFeed model={model} />}
      </div>

      {selectedSystem && (
        <SystemDrawer
          system={selectedSystem}
          viewMode={viewMode}
          onClose={() => setSelectedSystemId(null)}
          onSelectSystem={(id) => setSelectedSystemId(id)}
        />
      )}
    </div>
  );
}

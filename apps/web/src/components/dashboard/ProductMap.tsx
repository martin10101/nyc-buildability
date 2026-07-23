'use client';

import type { DashboardModel, SystemModel } from '@/lib/dashboard/types';
import { healthMeta } from './ui';

const NODE_W = 168;
const NODE_H = 74;
const GAP_X = 56;
const GAP_Y = 26;
const PAD = 16;

function computeDepths(systems: SystemModel[]): Map<string, number> {
  const byId = new Map(systems.map((s) => [s.id, s]));
  const depth = new Map<string, number>();
  const visiting = new Set<string>();
  const calc = (id: string): number => {
    if (depth.has(id)) return depth.get(id)!;
    if (visiting.has(id)) return 0; // cycle guard
    visiting.add(id);
    const s = byId.get(id);
    const deps = (s?.dependsOn ?? []).filter((d) => byId.has(d));
    const d = deps.length === 0 ? 0 : 1 + Math.max(...deps.map(calc));
    visiting.delete(id);
    depth.set(id, d);
    return d;
  };
  for (const s of systems) calc(s.id);
  return depth;
}

export function ProductMap({
  model, onSelectSystem,
}: {
  model: DashboardModel;
  onSelectSystem: (id: string) => void;
}) {
  const systems = model.systems;
  const depth = computeDepths(systems);
  const maxDepth = Math.max(0, ...[...depth.values()]);

  // group by depth, stable order by id within a layer
  const layers: SystemModel[][] = [];
  for (let d = 0; d <= maxDepth; d++) {
    layers[d] = systems
      .filter((s) => depth.get(s.id) === d)
      .sort((a, b) => a.id.localeCompare(b.id));
  }
  const maxLayer = Math.max(1, ...layers.map((l) => l.length));

  const pos = new Map<string, { x: number; y: number }>();
  layers.forEach((layer, d) => {
    layer.forEach((s, i) => {
      pos.set(s.id, { x: PAD + d * (NODE_W + GAP_X), y: PAD + i * (NODE_H + GAP_Y) });
    });
  });

  const width = PAD * 2 + (maxDepth + 1) * NODE_W + maxDepth * GAP_X;
  const height = PAD * 2 + maxLayer * NODE_H + (maxLayer - 1) * GAP_Y;

  const edges: Array<{ from: string; to: string }> = [];
  for (const s of systems) {
    for (const dep of s.dependsOn) {
      if (pos.has(dep) && pos.has(s.id)) edges.push({ from: dep, to: s.id });
    }
  }

  return (
    <div>
      <p className="dash-map-hint">
        How the systems connect (left → right = the architect journey). Colour shows health;
        every node is also labelled. Select a system for detail. Scroll sideways to see all.
      </p>
      <div className="dash-map-scroll table-scroll">
        <svg
          className="dash-map-svg"
          viewBox={`0 0 ${width} ${height}`}
          width={width}
          height={height}
          role="group"
          aria-label="Product system dependency map"
        >
          <defs>
            <marker id="dash-arrow" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto">
              <path d="M0,0 L8,4 L0,8 Z" className="dash-edge-head" />
            </marker>
          </defs>
          {edges.map((e, i) => {
            const a = pos.get(e.from)!;
            const b = pos.get(e.to)!;
            const x1 = a.x + NODE_W;
            const y1 = a.y + NODE_H / 2;
            const x2 = b.x;
            const y2 = b.y + NODE_H / 2;
            const mx = (x1 + x2) / 2;
            return (
              <path
                key={i}
                d={`M ${x1} ${y1} C ${mx} ${y1}, ${mx} ${y2}, ${x2} ${y2}`}
                className="dash-edge"
                markerEnd="url(#dash-arrow)"
                fill="none"
              />
            );
          })}
          {systems.map((s) => {
            const p = pos.get(s.id)!;
            const hm = healthMeta(s.health);
            const eng = s.engCompletion === null ? null : Math.round(s.engCompletion * 100);
            const label = `${s.name}. Health ${hm.label}. ${eng === null ? 'completion unknown' : eng + ' percent built'}. ${s.criticalForBeta ? 'Critical for beta.' : ''}`;
            return (
              <g
                key={s.id}
                transform={`translate(${p.x} ${p.y})`}
                role="button"
                tabIndex={0}
                aria-label={label}
                className={`dash-node ${hm.cls}`}
                onClick={() => onSelectSystem(s.id)}
                onKeyDown={(ev) => {
                  if (ev.key === 'Enter' || ev.key === ' ') { ev.preventDefault(); onSelectSystem(s.id); }
                }}
              >
                <rect width={NODE_W} height={NODE_H} rx={10} className="dash-node-rect" />
                {s.criticalForBeta && <rect width={4} height={NODE_H} rx={2} className="dash-node-critical" />}
                <text x={12} y={22} className="dash-node-title">
                  {s.name.length > 22 ? s.name.slice(0, 21) + '…' : s.name}
                </text>
                <text x={12} y={40} className="dash-node-sub">
                  <tspan aria-hidden="true">{hm.symbol}</tspan> {hm.label}
                  {eng !== null ? ` · ${eng}% built` : ' · unknown'}
                </text>
                <rect x={12} y={NODE_H - 16} width={NODE_W - 24} height={5} rx={2.5} className="dash-node-track" />
                <rect x={12} y={NODE_H - 16} width={(NODE_W - 24) * (eng ?? 0) / 100} height={5} rx={2.5} className="dash-node-bar" />
              </g>
            );
          })}
        </svg>
      </div>

      <ul className="dash-map-legend" aria-label="Legend">
        <li><span aria-hidden="true" className="dash-health dash-h-green">●</span> Healthy</li>
        <li><span aria-hidden="true" className="dash-health dash-h-yellow">◑</span> Attention</li>
        <li><span aria-hidden="true" className="dash-health dash-h-red">▲</span> Problem</li>
        <li><span aria-hidden="true" className="dash-health dash-h-unknown">?</span> Unknown</li>
        <li><span aria-hidden="true" className="dash-legend-critical" /> Critical for beta</li>
      </ul>
    </div>
  );
}

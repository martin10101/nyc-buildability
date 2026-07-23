'use client';

import type { DashboardModel, Task } from '@/lib/dashboard/types';
import { StatusBadge } from './ui';

function GateChecklist({ task }: { task: Task }) {
  if (task.requiredGates.length === 0) return null;
  return (
    <ul className="dash-gates" aria-label="Required gates">
      {task.requiredGates.map((g) => {
        const passed = task.passedGates.includes(g);
        return (
          <li key={g} className={passed ? 'dash-gate-done' : 'dash-gate-pending'}>
            <span aria-hidden="true">{passed ? '✓' : '○'}</span> {g}
            <span className="visually-hidden">{passed ? ' passed' : ' pending'}</span>
          </li>
        );
      })}
    </ul>
  );
}

function TaskCard({ task, viewMode, onSelectSystem, primary = false }: {
  task: Task; viewMode: 'owner' | 'technical'; onSelectSystem: (id: string) => void; primary?: boolean;
}) {
  return (
    <div className={`dash-taskcard ${primary ? 'dash-taskcard-primary' : ''}`}>
      <div className="dash-taskcard-head">
        <span className="dash-mono">{task.id}</span>
        <StatusBadge status={task.ownerStatus} />
      </div>
      <div className="dash-taskcard-title">{task.ownerTitle ?? task.title}</div>
      {task.ownerDescription && <p className="dash-taskcard-desc">{task.ownerDescription}</p>}
      <GateChecklist task={task} />
      {task.acceptanceBlockers.length > 0 && (
        <p className="dash-muted dash-small">Before acceptance: {task.acceptanceBlockers.join('; ')}.</p>
      )}
      {task.reconciliationNote && (
        <p className="dash-note-honest">Status note: {task.reconciliationNote}</p>
      )}
      {viewMode === 'technical' && (
        <dl className="dash-tech">
          {task.branch && (<><dt>Branch</dt><dd className="dash-mono">{task.branch}</dd></>)}
          {task.prNumber && (<><dt>PR</dt><dd>#{task.prNumber}</dd></>)}
          <dt>Milestone</dt><dd className="dash-mono">{task.milestoneId}</dd>
          {task.systemId && (<><dt>System</dt>
            <dd><button className="dash-link" type="button" onClick={() => onSelectSystem(task.systemId!)}>{task.systemId}</button></dd></>)}
          {task.dependencies.length > 0 && (<><dt>Depends on</dt><dd className="dash-mono">{task.dependencies.join(', ')}</dd></>)}
        </dl>
      )}
    </div>
  );
}

export function CurrentWork({
  model, viewMode, onSelectSystem,
}: {
  model: DashboardModel; viewMode: 'owner' | 'technical'; onSelectSystem: (id: string) => void;
}) {
  const { activeTasks, primary, next } = model.currentWork;
  const others = activeTasks.filter((t) => t.id !== primary?.id);

  return (
    <div>
      <section className="dash-card" aria-labelledby="dash-cw-primary">
        <h2 id="dash-cw-primary" className="dash-card-title">What's being worked on now</h2>
        {primary ? (
          <TaskCard task={primary} viewMode={viewMode} onSelectSystem={onSelectSystem} primary />
        ) : (
          <p className="dash-muted">No task is currently in an active lifecycle state.</p>
        )}
        {others.length > 0 && (
          <>
            <h3 className="dash-subhead">Also active ({others.length})</h3>
            <div className="dash-taskgrid">
              {others.map((t) => (
                <TaskCard key={t.id} task={t} viewMode={viewMode} onSelectSystem={onSelectSystem} />
              ))}
            </div>
          </>
        )}
      </section>

      <section className="dash-card" aria-labelledby="dash-cw-next">
        <h2 id="dash-cw-next" className="dash-card-title">Next up</h2>
        {next.length === 0 ? (
          <p className="dash-muted">No unblocked task is ready to start next.</p>
        ) : (
          <ul className="dash-next">
            {next.map((t) => (
              <li key={t.id}>
                <span className="dash-mono">{t.id}</span> — {t.ownerTitle ?? t.title}
                <StatusBadge status={t.ownerStatus} />
              </li>
            ))}
          </ul>
        )}
      </section>
    </div>
  );
}

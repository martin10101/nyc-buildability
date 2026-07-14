#!/usr/bin/env python3
"""Minimal deterministic task/gate/checkpoint control plane for Claude agents."""
from __future__ import annotations
import argparse, datetime as dt, json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PC = ROOT / "project-control"

def now(): return dt.datetime.now(dt.timezone.utc).isoformat()
def load(path): return json.loads(path.read_text(encoding="utf-8-sig"))
def save(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    data["updated_at"] = now()
    path.write_text(json.dumps(data, indent=2, sort_keys=False) + "\n", encoding="utf-8")
def task_path(task_id): return PC / "tasks" / f"{task_id}.json"
def report_path(task_id): return PC / "reports" / f"{task_id}.json"

def init(_):
    for d in ["tasks","reports","gates","checkpoints","blockers"]:
        (PC/d).mkdir(parents=True, exist_ok=True)
    required = [PC/"master_plan.json", PC/"state.json", PC/"config.json"]
    missing = [str(p) for p in required if not p.exists()]
    if missing:
        print("Missing control files:\n" + "\n".join(missing), file=sys.stderr); return 2
    print("Project control plane ready."); return 0

def new_task(a):
    p = task_path(a.task_id)
    if p.exists():
        print(f"Task exists: {a.task_id}", file=sys.stderr); return 2
    config = load(PC/"config.json")
    gates = a.gates.split(",") if a.gates else config["required_gates_by_task_type"].get(a.task_type,["G0","G2","G3","G4"])
    data = {
      "task_id":a.task_id,"title":a.title,"task_type":a.task_type,"milestone_id":a.milestone,
      "objective":a.objective,"business_reason":a.business_reason or "","inputs":[],"outputs":[],
      "dependencies":[x for x in (a.depends or "").split(",") if x],"allowed_paths":[],"forbidden_paths":[],
      "acceptance_scenarios":[],"required_gates":gates,"producer_agent":None,"reviewer_agents":[],
      "status":"backlog","progress_percent":0,"risks":[],"blockers":[],"created_at":now(),"updated_at":now()
    }
    save(p,data); print(p.relative_to(ROOT)); return 0

def claim(a):
    p=task_path(a.task_id); t=load(p)
    if t["status"] not in ["ready","backlog","rework"]:
        print(f"Cannot claim from status {t['status']}",file=sys.stderr); return 2
    t.update({"producer_agent":a.agent,"worktree":a.worktree,"status":"claimed","progress_percent":10})
    save(p,t); print(f"Claimed {a.task_id} by {a.agent}"); return 0

def progress(a):
    p=task_path(a.task_id); t=load(p)
    if a.percent >= 100:
        print("Only orchestrator acceptance may set 100%.",file=sys.stderr); return 2
    t["progress_percent"]=a.percent; t["status"]=a.status or t["status"]
    t.setdefault("progress_log",[]).append({"at":now(),"agent":a.agent,"percent":a.percent,"message":a.message})
    save(p,t); print(f"Updated {a.task_id} to {a.percent}%"); return 0

def submit(a):
    p=task_path(a.task_id); t=load(p)
    rp=Path(a.report)
    if not rp.exists(): print("Report file missing",file=sys.stderr); return 2
    report={"task_id":a.task_id,"producer_agent":a.agent,"report_file":str(rp),"submitted_at":now(),"requested_status":a.requested_status}
    save(report_path(a.task_id),report)
    if a.requested_status=="awaiting_gate": t["status"]="awaiting_gate"; t["progress_percent"]=85
    elif a.requested_status=="blocked": t["status"]="blocked"
    else: t["status"]="rework"
    save(p,t); print(f"Submitted {a.task_id}: {a.requested_status}"); return 0

def gate(a):
    p=task_path(a.task_id); t=load(p)
    if t.get("producer_agent")==a.reviewer:
        print("Producer cannot independently gate own task.",file=sys.stderr); return 2
    rp=Path(a.report)
    if not rp.exists(): print("Gate report missing",file=sys.stderr); return 2
    gp=PC/"gates"/f"{a.task_id}-{a.gate_id}.json"
    save(gp,{"task_id":a.task_id,"gate_id":a.gate_id,"reviewer":a.reviewer,"result":a.result,"report_file":str(rp),"reviewed_at":now()})
    if a.result=="FAIL": t["status"]="rework"
    elif a.result=="BLOCKED": t["status"]="blocked"
    else:
        passed={load(x).get("gate_id") for x in (PC/"gates").glob(f"{a.task_id}-G*.json") if load(x).get("result")=="PASS"}
        required=set(t.get("required_gates",[]))
        if a.gate_id == "G0" and t.get("status") in ["backlog", "rework"]:
            t["status"]="ready"; t["progress_percent"]=max(t.get("progress_percent",0),5)
        else:
            t["status"]="awaiting_gate"; t["progress_percent"]=95 if required.issubset(passed) else max(t.get("progress_percent",0),85)
    save(p,t); print(f"Recorded {a.gate_id} {a.result} for {a.task_id}"); return 0

def accept(a):
    p=task_path(a.task_id); t=load(p)
    if a.agent!="orchestrator": print("Only orchestrator may accept.",file=sys.stderr); return 2
    passed={load(x).get("gate_id") for x in (PC/"gates").glob(f"{a.task_id}-G*.json") if load(x).get("result")=="PASS"}
    missing=set(t.get("required_gates",[]))-passed
    if missing: print("Missing passing gates: "+", ".join(sorted(missing)),file=sys.stderr); return 2
    t["status"]="accepted"; t["progress_percent"]=100; t["accepted_by"]=a.agent; t["accepted_at"]=now(); save(p,t)
    print(f"Accepted {a.task_id}"); return 0

def checkpoint(a):
    state=load(PC/"state.json")
    cp_id=a.checkpoint_id
    cp={"checkpoint_id":cp_id,"timestamp":now(),"commit":a.commit,"branch":a.branch,"active_milestone":state.get("current_milestone"),"summary":a.summary}
    save(PC/"checkpoints"/f"{cp_id}.json",cp); state["last_checkpoint"]=cp_id; save(PC/"state.json",state)
    print(f"Checkpoint {cp_id}"); return 0

def status(_):
    plan=load(PC/"master_plan.json"); tasks=[]
    for p in sorted((PC/"tasks").glob("*.json")): tasks.append(load(p))
    counts={}
    for t in tasks: counts[t["status"]]=counts.get(t["status"],0)+1
    print(json.dumps({"current_milestone":plan.get("current_milestone"),"milestones":plan.get("milestones",[]),"task_counts":counts,"tasks":[{"id":t["task_id"],"status":t["status"],"progress":t["progress_percent"],"agent":t.get("producer_agent")} for t in tasks]},indent=2)); return 0

def main():
    p=argparse.ArgumentParser(); sp=p.add_subparsers(dest="cmd",required=True)
    x=sp.add_parser("init"); x.set_defaults(fn=init)
    x=sp.add_parser("new-task");
    for n,kw in [("--task-id",{"required":True}),("--title",{"required":True}),("--task-type",{"required":True}),("--milestone",{"required":True}),("--objective",{"required":True}),("--business-reason",{}),("--depends",{}),("--gates",{})]: x.add_argument(n,**kw)
    x.set_defaults(fn=new_task)
    x=sp.add_parser("claim"); x.add_argument("--task-id",required=True); x.add_argument("--agent",required=True); x.add_argument("--worktree",required=True); x.set_defaults(fn=claim)
    x=sp.add_parser("progress"); x.add_argument("--task-id",required=True); x.add_argument("--agent",required=True); x.add_argument("--percent",type=int,required=True); x.add_argument("--status"); x.add_argument("--message",required=True); x.set_defaults(fn=progress)
    x=sp.add_parser("submit"); x.add_argument("--task-id",required=True); x.add_argument("--agent",required=True); x.add_argument("--report",required=True); x.add_argument("--requested-status",choices=["awaiting_gate","blocked","needs_split"],required=True); x.set_defaults(fn=submit)
    x=sp.add_parser("gate"); x.add_argument("--task-id",required=True); x.add_argument("--gate-id",required=True); x.add_argument("--reviewer",required=True); x.add_argument("--result",choices=["PASS","FAIL","BLOCKED"],required=True); x.add_argument("--report",required=True); x.set_defaults(fn=gate)
    x=sp.add_parser("accept"); x.add_argument("--task-id",required=True); x.add_argument("--agent",required=True); x.set_defaults(fn=accept)
    x=sp.add_parser("checkpoint"); x.add_argument("--checkpoint-id",required=True); x.add_argument("--commit",required=True); x.add_argument("--branch",required=True); x.add_argument("--summary",required=True); x.set_defaults(fn=checkpoint)
    x=sp.add_parser("status"); x.set_defaults(fn=status)
    a=p.parse_args(); raise SystemExit(a.fn(a))
if __name__=="__main__": main()

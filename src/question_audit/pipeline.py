from __future__ import annotations
import argparse
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone

from .io import load_json, read_jsonl, append_jsonl, write_json
from .model import solve
from .normalize import question_payload
from .prompts import build_prompt
from .rules import aggregate_passes, deterministic_answer, hard_gate


def utcnow():
    return datetime.now(timezone.utc).isoformat()


def process_question(question: dict, discipline: dict, cfg: dict, model: str) -> dict:
    qid = str(question.get("id"))
    hard_status, hard_flags = hard_gate(question, cfg.get("hold_images_by_default", True))
    if hard_status:
        return {
            "question_id":qid,
            "status":hard_status,
            "answer_letter":None,
            "confidence":1.0,
            "evidence":"HARD_GATE",
            "flags":hard_flags,
            "processed_at":utcnow(),
        }

    known = deterministic_answer(question)
    payload = question_payload(question)
    if known:
        prompt = build_prompt(payload, discipline, 0)
        sem = solve(prompt, model)
        return {
            "question_id":qid,
            "status":"AUTO_READY",
            "answer_letter":known["letter"],
            "confidence":known["confidence"],
            "evidence":known["evidence"],
            "door_id":sem.get("door_id"),
            "subtopic":sem.get("subtopic"),
            "flags":sem.get("flags") or [],
            "passes":[sem],
            "processed_at":utcnow(),
        }

    passes=[]
    for i in range(int(cfg.get("passes",3))):
        prompt=build_prompt(payload, discipline, i)
        passes.append(solve(prompt, model))

    agg=aggregate_passes(
        passes,
        float(cfg.get("auto_ready_min_confidence",0.80)),
        float(cfg.get("review_min_confidence",0.65)),
    )
    agg.update({
        "question_id":qid,
        "evidence":"MODEL_CONSENSUS_3X" if agg["status"]=="AUTO_READY" else "MODEL_REVIEW",
        "processed_at":utcnow(),
    })
    return agg


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--input",default="data/raw/sociology_questions_5170.json")
    ap.add_argument("--discipline",default="config/disciplines/sociology.json")
    ap.add_argument("--config",default="config/pipeline.json")
    ap.add_argument("--state",default="data/state/results.jsonl")
    ap.add_argument("--summary",default="data/output/summary.json")
    ap.add_argument("--limit",type=int,default=None)
    ap.add_argument("--retry-status",action="append",default=[], choices=["REVIEW","HOLD"])
    ap.add_argument("--max-attempts",type=int,default=None)
    args=ap.parse_args()

    questions=load_json(args.input)
    discipline=load_json(args.discipline)
    cfg=load_json(args.config)
    model=os.environ.get("OPENAI_MODEL",cfg.get("model_default","gpt-5-mini"))
    limit=args.limit or int(os.environ.get("BATCH_SIZE",cfg.get("batch_size",80)))

    previous=read_jsonl(args.state)
    latest={r["question_id"]:r for r in previous if r.get("question_id")}
    attempts={}
    for row in previous:
        qid=row.get("question_id")
        if qid:
            attempts[qid]=attempts.get(qid,0)+1
    retry_statuses=set(args.retry_status or [])
    max_attempts=args.max_attempts or int(cfg.get("max_attempts_per_question",3))

    pending=[]
    for q in questions:
        qid=str(q.get("id"))
        if qid not in latest:
            pending.append(q)
        elif latest[qid].get("status") in retry_statuses and attempts.get(qid,0) < max_attempts:
            pending.append(q)
        if len(pending)>=limit:
            break

    if not pending:
        print("No pending questions.")
    else:
        workers=int(os.environ.get("MAX_WORKERS",cfg.get("max_workers",4)))
        with ThreadPoolExecutor(max_workers=workers) as pool:
            futures={pool.submit(process_question,q,discipline,cfg,model):str(q.get("id")) for q in pending}
            for fut in as_completed(futures):
                qid=futures[fut]
                try:
                    row=fut.result()
                except Exception as exc:
                    row={
                        "question_id":qid,
                        "status":"REVIEW",
                        "answer_letter":None,
                        "confidence":0.0,
                        "evidence":"PIPELINE_ERROR",
                        "flags":["pipeline_error"],
                        "error":repr(exc),
                        "processed_at":utcnow(),
                    }
                append_jsonl(args.state,row)
                latest[qid]=row
                print(qid,row["status"],row.get("answer_letter"),row.get("confidence"))

    counts={}
    for row in latest.values():
        counts[row.get("status","UNKNOWN")]=counts.get(row.get("status","UNKNOWN"),0)+1
    write_json(args.summary,{
        "total_input":len(questions),
        "processed_unique":len(latest),
        "remaining":max(0,len(questions)-len(latest)),
        "status_counts":counts,
        "model":model,
        "updated_at":utcnow(),
    })

if __name__=="__main__":
    main()

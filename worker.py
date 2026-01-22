#!/usr/bin/env python3
"""Entrypoint para ECS: consome mensagens do SQS e importa .mpp no Postgres."""

from __future__ import annotations

from mpxj_pm.sqs_worker import run_worker


if __name__ == "__main__":
    raise SystemExit(run_worker())

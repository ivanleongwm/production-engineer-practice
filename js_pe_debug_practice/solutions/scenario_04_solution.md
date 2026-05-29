# Scenario 04 Solution - Missing Execution Report

## Commands you should run

- `grep -Rni "O4004\\|E5404" logs/`
- `grep -Rni "publish_failed\\|kafka_topic_not_found\\|topic_missing" logs/`
- `less logs/engine.log`
- `less logs/execution_publisher.log`
- `less logs/system.log`

## Log lines that matter

- `engine.log`: fill generated successfully (`exec_id=E5404`)
- `execution_publisher.log`: `publish_failed ... kafka_topic_not_found`
- `system.log`: dependency error on missing Kafka topic
- `client.log`: still waiting for execution

## First divergence

At execution publication. Fill exists, but report cannot be published downstream.

## Likely root cause

Misconfigured/missing Kafka topic (`exec.reports.v2`) in execution publisher dependency.

## Interview explanation

"I validated that matching engine generated a fill, so trading core succeeded. Failure appears when publishing execution reports: explicit topic-not-found errors plus system dependency alarms. Root cause is messaging config/infra, not order matching."

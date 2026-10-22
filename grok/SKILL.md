# Velocity hour

Use the velocity package at `/workspace/velocity`. Import it with `/workspace` on the Python path. The package does not call X. This skill does not post.

Run this skill once an hour. The hourly routine is the clock. It is not a script.

Read the observation text at `/workspace/faucet/observations.jsonl`. Read the label log at `/workspace/labeler/labels.jsonl`. Create either file, and its directory, when it is missing.

Read the signed-in account's home timeline. Do not pass a keyword. Do not turn a trend name into a search. Leave news off unless you were explicitly given a topic.

A one-snapshot post is a post id with exactly one complete line in the observation file. Look up each one-snapshot post by id. Also look up each post id on a waiting label whose check time is at or before the current UTC second. Request `public_metrics`. Stamp each read with its own UTC time, `YYYY-MM-DDTHH:MM:SSZ`, on `fetched_at`. On HTTP 429, stop looking up more posts.

Call `run_hour` from `velocity.hour` with the observation text, the label-log text, the timeline payload, the by-id payload, and the current UTC time as `YYYY-MM-DDTHH:MM:SSZ`. The by-id payload is a JSON object keyed by post id, or a response with `data` and `errors`. Write the returned observation text back to `/workspace/faucet/observations.jsonl`. Write the returned label text back to `/workspace/labeler/labels.jsonl`.

`run_hour` appends timeline posts as snapshots, appends a second snapshot for a one-snapshot post when that id is in the by-id payload, and appends one `waiting` claim per count that rose. It does not append a claim whose identity is already in the log. The identity is `rule_id`, post id, metric key, comparison, integer threshold, and check time. The rule id is `velocity-` plus the count name.

The first terminal grade wins. A rate-limit result stops the grading pass and leaves the remaining due labels `waiting`.

Return the four counts `waiting`, `matched`, `missed`, and `unavailable` for every `rule_id` in the log. Include the hit rate when `matched` plus `missed` is at least 1. Otherwise say no rate. Do not delete a rule.

Do not post, like, follow, or reply.

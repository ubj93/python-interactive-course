# Syllabus

Thirteen parts. Parts 1–8 are the language, in the order the Helsinki MOOC and MIT
6.0001 teach it, compressed for someone who has programmed before. Parts 9–11 are the
standard-library toolkit a Client Platform Engineer uses daily. Part 12 is the
interview-pattern drill. Part 13 is a set of timed capstones shaped like real take-home
and on-site problems for CPE roles.

Each line: `id slug (kyu)` and what it drills. Slugs are folder names and function names.

## Part 1 · Foundations: values, strings, decisions
1. greet_device (8) f-strings
2. normalize_hostname (8) chained string methods
3. disk_status (8) thresholds, early return, None
4. os_family (8) substring tests, priority order
5. bytes_to_human (7) loop + format spec
6. is_valid_serial (7) validation with string methods

## Part 2 · Loops and lists
1. count_online (8) for loop with a condition over a list of dicts
2. oldest_device (7) track a running best; empty list returns None
3. chunk_serials (7) slice a list into fixed-size batches (last one shorter)
4. dedupe_preserve_order (7) remove duplicates keeping first occurrence
5. rolling_average (6) window average over cpu samples; windows shorter than n at the start
6. find_gaps (6) missing integers in a sorted list of asset tags, as (start, end) ranges
7. top_n_by_memory (6) sorted with key, reverse, ties by name

## Part 3 · Functions and modules
1. build_command (7) defaults and keyword arguments; returns list of argv strings
2. retry_policy (6) **kwargs with validation and defaults, returns dict
3. parse_flags (6) *args of "--key=value"/"--flag" strings into a dict
4. compose (6) higher-order: compose(f, g)(x) == f(g(x)); variadic
5. apply_pipeline (6) list of callables applied in order, with early stop on None
6. make_counter (5) closures: returns a function with private state (nonlocal)

## Part 4 · Strings and regular expressions
1. parse_kv_line (7) "key=value; key2=value2" into a dict, whitespace tolerant
2. snake_to_camel (7) and back; str.title pitfalls
3. extract_ips (6) re.findall for IPv4, validate octets
4. mask_secrets (6) re.sub with a callable, keep last 4 chars of tokens
5. parse_version_string (6) "14.5.1 (23F79)" -> tuple + build; missing parts default 0
6. parse_syslog_line (5) named groups; timestamp, host, process, pid, message
7. render_table (6) column alignment with format specs; widths from data

## Part 5 · Dictionaries and sets
1. count_by_os (7) counting with dict.get / setdefault
2. group_by_department (6) dict of lists, stable order
3. invert_index (6) user -> devices to device -> user, detect duplicates
4. fleet_diff (6) set operations: in MDM not inventory, both, neither; returns sorted lists
5. most_common_apps (6) top k with ties broken alphabetically
6. merge_configs (5) recursive deep merge, later wins, lists replaced not merged
7. flatten_dict (5) nested dict -> "a.b.c" keys; and unflatten

## Part 6 · Files and data formats
1. read_hostnames (7) read a file, strip, skip blanks and # comments
2. count_log_levels (6) count ERROR/WARN/INFO from a log file, streaming line by line
3. load_inventory_csv (6) csv.DictReader, type conversion, skip malformed rows
4. write_report_json (6) json.dump with indent and sorted keys, round-trip
5. tail_lines (6) last n lines of a file without reading it all into memory (deque)
6. parse_profile_plist (5) plistlib: configuration profile payloads -> summary dict
7. find_large_files (5) pathlib.rglob with size threshold and suffix filter, sorted by size

## Part 7 · Errors and robustness
1. safe_int (7) try/except ValueError/TypeError with a default
2. parse_port (6) raise ValueError with a helpful message for range/format errors
3. ConfigError (6) custom exception hierarchy with attributes; raise from
4. read_json_or_default (6) FileNotFoundError vs JSONDecodeError handled differently
5. validate_device_record (5) collect all errors instead of stopping at the first
6. retry (5) decorator that retries on given exceptions with injected sleep; re-raises after n

## Part 8 · Classes and dataclasses
1. Device (6) __init__, __repr__, __eq__, a method
2. Ticket (6) @dataclass with order=True and field defaults; sort by priority then created
3. Platform (6) Enum with a from_string classmethod that tolerates aliases
4. Inventory (5) container class: add, get, remove, __len__, __iter__, __contains__
5. Version (4) comparable class: parse "1.2.10", __lt__/__eq__, functools.total_ordering
6. TokenBucket (5) rate limiter with injected clock; allow(), refill logic

## Part 9 · Comprehensions, iterators, functional tools
1. stale_devices (7) list comprehension with a condition and a cutoff date
2. batched (6) generator yielding fixed-size tuples from any iterable
3. read_lines_lazy (6) generator over a file object that strips and skips comments
4. sort_devices (5) multi-key sort: os asc, last_seen desc, name asc; key functions
5. pairwise_deltas (6) zip(xs, xs[1:]) / itertools; time between check-ins
6. group_consecutive (5) itertools.groupby on sorted data; runs of failing builds
7. top_k (5) heapq.nlargest with a key vs full sort; explain the trade-off

## Part 10 · Standard-library toolkit
1. days_since (6) datetime parsing ISO 8601 with Z, timezone aware, injected now
2. parse_args (6) argparse: subcommands not required; flags, types, defaults; returns Namespace
3. checksum_file (6) hashlib sha256 in chunks; hexdigest; compare to expected
4. run_command (5) subprocess wrapper with an injected runner; parse stdout, non-zero exit
5. recent_events (5) collections.deque(maxlen) sliding window with counts
6. build_adjacency (6) collections.defaultdict(set) from edge list; undirected
7. most_common_with_ties (6) Counter.most_common and stable tie handling

## Part 11 · HTTP APIs (with a fake client)
1. build_headers (7) bearer token, accept, user-agent; None token omitted
2. parse_rate_limit (6) headers -> remaining, reset seconds; missing headers
3. fetch_all_pages (5) follow `next` cursor until exhausted; guard against loops
4. retry_with_backoff (5) exponential backoff with jitter=0 for tests, injected sleep, retry on 429/5xx
5. verify_webhook_signature (5) hmac.compare_digest over body with a shared secret
6. sync_devices (4) diff local vs remote, produce create/update/delete calls via fake client

## Part 12 · Interview patterns
1. two_sum (6) hash map, one pass
2. balanced_brackets (6) stack
3. anagram_groups (5) canonical key grouping
4. longest_unique_window (5) sliding window
5. merge_intervals (5) sort then sweep; maintenance windows
6. word_frequency_top_k (5) Counter + heap, ties alphabetical
7. bisect_first_bad (5) binary search with an injected is_bad predicate, minimal calls
8. dir_sizes (5) recursion over a nested dict tree; total sizes per folder
9. install_order (4) topological sort over package dependencies, detect cycles
10. LRUCache (4) OrderedDict or dict + move_to_end; get/put O(1)

## Part 13 · Capstones (timed, 3–4 kyu)
1. stale_device_report (4) CSV in, grouped markdown report out; cutoff rules
2. log_triage (4) parse mixed-format lines, bucket by error class, top offenders
3. config_drift (4) expected vs actual nested configs, path-addressed diff
4. enrollment_reconciler (3) three sources (MDM, directory, inventory) -> actions list
5. rollout_planner (3) ring-based rollout with percentages, blockers, and holds
6. manifest_resolver (3) Munki-style manifests with includes, managed installs/uninstalls, conflicts

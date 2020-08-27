# awscli scripts

Helper CLI to simplify mundane, repetitive awscli tasks.

Primary use-case: run on clients (i.e., laptops or workstations). Primarily
tested on OSX as this is what my notebook is.

However, there's no reason to believe why these bash scripts can't run on
EC2+Linux, otherwise we welcome your bug reports or PRs.

## What's in here

`ccls` to list all CodeCommit repos.

`smnb-*` to start, stop, check status, and get presigned url of a classic
SageMaker notebook instance. Note that `smnb-*` are symlinks to `smnb-base`.

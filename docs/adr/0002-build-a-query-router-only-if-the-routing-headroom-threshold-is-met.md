# Build a query router only if the pre-registered routing headroom threshold is met

The goal is a system that indexes several chunkings and routes each query to the one that suits it. Before building that router, v1 measures the best single chunking and the routing headroom over it: how much an oracle router, which picks the best chunking per question in hindsight, beats the best single chunking at the same token budget. No real router can beat the oracle, so a small headroom means routing is not worth building.

A router is built in v2 only if the routing headroom on the production line, in the production view, is at least +0.05 retrieval recall at the same token budget, with a 95% confidence interval that excludes 0. The interval comes from a paired bootstrap that resamples documents rather than questions, because questions about the same document are not independent and resampling them one by one would make the interval too narrow.

The threshold and the statistic are fixed before any result is seen. An oracle router is biased upwards by construction (it takes the maximum over every chunking for every question), so with enough chunkings some headroom always appears; choosing the bar after looking at the numbers would let that noise decide whether to build a router.

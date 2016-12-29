Algorithms on graphs
====================

# What I learned from week 6

Week six is about implementing the following concepts:

1. Bidirectional Dijkstra
2. Bidirectional AStar
3. Landmarks
4. Contraction Hierarchies

The following are my "Nota Bene"s that I made when I was implementing these
algorithms.

* Be sure to not overflow. Use Len (long long) consistently. Using double
  for Len may give you wrong results.

* Do not use INFINITY as a constant name, gcc 5.2 will complain. I used
  VERY_LARGE instead.

* Make sure that your VERY_LARGE is equal to max/4. max/2 is required because
  you search in two directions. Another max/2 is required because ... why?
  FIXME.

* Use separate flag array of visited_ for each direction because you need to
  check whether only other side has reached a vertice (this may not be necessary
  depending on your stopping condition).

* Spend time to prepare unit tests, write helpers to generate graphs of
  certain shapes, add tools to visualize your results. Start with simple
  cases, put them into stone (test cases), grow complexity further.

* Implement one-directional Dijkstra as a baseline for correctness and
  performance.

* Be sure to mark vertice as visited at the right moment. Specifically,
  mark vertice as visited only after all its neighbors are traversed.

* Be sure to write potential function correctly. Check that required condition
  holds true on all vertices.

* Be sure to use modified edge weight (distance estimate by potential
  function) correctly. Namely, estimate is ONLY used to prioritize vertices
  in a queue (front). DO NOT USE estimate when saving best distance values,
  DO NOT USE it for comparison with current best distance!

* Pay attention to stopping conditions. For Bidirectional Dijkstra you may
  get away with simple check whether a vertice has been visited by the
  other direction. For Bidirectional AStar you need to bookkeep mu,
  and check top_f + top_r >= mu after every iteration.

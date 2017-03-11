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

* When front queues are exhausted, make sure to check whether there has been
  any path found, check mu. If there is, there is a short path.

* Add simple check in the beginning of the query to test whether
  source == target.


## QUERY RESULTS

22:20:54 bz.boltx64 » friend_suggestion 1 → time pypy3 stress.py --random-queries 0 < test_astar/usa-road.in 2>/dev/null 
Preprocessing landmarks [4362, 58197, 79224, 191500]
Loaded landmarks from untracked/astar/landmarks.pkl.cache
Preprocessed 4 landmarks
Preprocessing landmarks [4362, 58197, 79224, 191500]
Loaded landmarks from untracked/astar/landmarks.pkl.cache
Preprocessed 4 landmarks
                 BFS   DijkOne  AStarOne    ALTOne    DijkBi   AStarBi     ALTBi    s -> t
             1328085   1328085   1328085   1328085   1328085   1328085   1328085   1 56854
  MISMATCH    145694    145694    145694    148376    145694    145694    145694 3214 5138
              143270    143270    143270    143270    143270    143270    143270 2201 3913
  MISMATCH    128130    128130    128130    128472    128130    128130    128472 3961 1786
  MISMATCH    175503    175503    175503    178026    175503    175503    175503 4902 2655
              301740    301740    301740    301740    301740    301740    301740   34 3453
               80593     80593     80593     80593     80593     80593     80593    1 3453
              210895    210895    210895    210895    210895    210895    210895  100 3453
              165748    165748    165748    165748    165748    165748    165748  200 3453
              154082    154082    154082    154082    154082    154082    154082  300 3453
              235219    235219    235219    235219    235219    235219    235219  400 3453
              152765    152765    152765    152765    152765    152765    152765  500 3453
               73350     73350     73350     73350     73350     73350     73350  600 3453
              115121    115121    115121    115121    115121    115121    115121 1000 3453
              138221    138221    138221    138221    138221    138221    138221 3000 3453
  MISMATCH    145694    145694    145694    148376    145694    145694    145694 3214 5138
              143270    143270    143270    143270    143270    143270    143270 2201 3913
  MISMATCH    128130    128130    128130    128472    128130    128130    128472 3961 1786
  MISMATCH    175503    175503    175503    178026    175503    175503    175503 4902 2655
              301740    301740    301740    301740    301740    301740    301740   34 3453
               80593     80593     80593     80593     80593     80593     80593    1 3453
              210895    210895    210895    210895    210895    210895    210895  100 3453
              165748    165748    165748    165748    165748    165748    165748  200 3453
              154082    154082    154082    154082    154082    154082    154082  300 3453
              235219    235219    235219    235219    235219    235219    235219  400 3453
              152765    152765    152765    152765    152765    152765    152765  500 3453
               73350     73350     73350     73350     73350     73350     73350  600 3453
              115121    115121    115121    115121    115121    115121    115121 1000 3453
              138221    138221    138221    138221    138221    138221    138221 3000 3453
  MISMATCH    160494    160494    160494    160494    160494    161001    160494  5139 885
                 BFS   DijkOne  AStarOne    ALTOne    DijkBi   AStarBi     ALTBi    s -> t
pypy3 stress.py --random-queries 0 < test_astar/usa-road.in 2> /dev/null  228.34s user 0.48s system 96% cpu 3:57.28 total


## QUERY EXECUTION TIMES (pypy)

22:17:38 bz.boltx64 » friend_suggestion → time pypy3 stress.py --random-queries 0 --profile --hide-results < test_astar/usa-road.in 2>/dev/null
Preprocessing landmarks [4362, 58197, 79224, 191500]
Loaded landmarks from untracked/astar/landmarks.pkl.cache
Preprocessed 4 landmarks
Preprocessing landmarks [4362, 58197, 79224, 191500]
Loaded landmarks from untracked/astar/landmarks.pkl.cache
Preprocessed 4 landmarks
                 BFS   DijkOne  AStarOne    ALTOne    DijkBi   AStarBi     ALTBi    s -> t
    <time>   7.68791   0.77079   0.88281   0.26785   0.45151   0.31159   0.30618
    <time>   6.72819   0.54953   0.66960   0.02259   0.02135   0.00814   0.01872
    <time>   5.52601   0.44743   0.67462   0.07293   0.00250   0.00154   0.01689
    <time>   6.89275   0.60797   0.52644   0.00635   0.00300   0.00120   0.00453
    <time>   4.64841   0.43366   0.68293   0.04009   0.00682   0.00847   0.02152
    <time>   4.91228   0.45074   0.69535   0.06871   0.01026   0.00330   0.01875
    <time>   7.63007   0.43401   0.50916   0.00760   0.00127   0.00101   0.00476
    <time>   7.01544   0.43012   0.49963   0.02080   0.00308   0.00169   0.00840
    <time>   5.87715   0.40689   0.52471   0.01027   0.00184   0.00147   0.00409
    <time>   5.79824   0.40948   0.53993   0.01294   0.00186   0.00142   0.00313
    <time>   9.13918   0.41525   0.70859   0.02330   0.00412   0.00327   0.02091
    <time>   6.13678   0.62195   0.51944   0.01532   0.00195   0.00160   0.00563
    <time>   5.79297   0.60309   0.50539   0.00116   0.00073   0.00073   0.00191
    <time>   8.40907   0.40732   0.56625   0.02146   0.00178   0.00154   0.00933
    <time>   7.44590   0.42739   0.50483   0.05416   0.00302   0.00253   0.02666
    <time>   6.68626   0.44872   0.64332   0.00971   0.00624   0.00154   0.00572
    <time>   6.03163   0.43680   0.67860   0.02162   0.00490   0.00145   0.01354
    <time>   7.10955   0.62379   0.59109   0.00417   0.00363   0.00129   0.00346
    <time>   4.96509   0.46999   0.68779   0.01668   0.00709   0.00322   0.01364
    <time>   4.85623   0.50697   0.69014   0.02304   0.00846   0.00295   0.01633
    <time>   7.61655   0.57527   0.54665   0.00414   0.00136   0.00127   0.00522
    <time>   7.13269   0.41088   0.53397   0.01162   0.00305   0.00194   0.00824
    <time>   5.94524   0.42918   0.53932   0.00871   0.00189   0.00133   0.00390
    <time>   5.89068   0.42396   0.50478   0.00812   0.00171   0.00143   0.00324
pypy3 stress.py --random-queries 0 --profile --hide-results <  2> /dev/null  187.72s user 0.33s system 96% cpu 3:15.31 total

## QUERY EXECUTION TIMES (python3)

22:45:26 bz.boltx64 » friend_suggestion 1 → time python stress.py --random-queries 0 --profile --hide-results < test_astar/usa-road.in 2>/dev/null
Preprocessing landmarks [4362, 58197, 79224, 191500]
Loaded landmarks from untracked/astar/landmarks.pkl.cache
Preprocessed 4 landmarks
Preprocessing landmarks [4362, 58197, 79224, 191500]
Loaded landmarks from untracked/astar/landmarks.pkl.cache
Preprocessed 4 landmarks
             DijkOne  AStarOne    ALTOne    DijkBi   AStarBi     ALTBi    s -> t
    <time>   3.29817   5.90689   0.59001   2.17007   1.20313   0.38343
    <time>   3.56023   6.02202   0.02089   0.18924   0.04630   0.02870
    <time>   3.48593   5.96014   0.02705   0.01701   0.01017   0.03909
    <time>   3.69461   6.21951   0.00608   0.02138   0.00817   0.01095
    <time>   3.56918   6.08143   0.01821   0.05103   0.02893   0.06390
    <time>   3.60630   5.98832   0.04233   0.06175   0.03218   0.09057
    <time>   3.48395   6.13712   0.01294   0.00907   0.00756   0.02220
    <time>   3.61572   6.03906   0.03160   0.01882   0.01514   0.03970
    <time>   3.60616   6.12585   0.02355   0.01299   0.01137   0.01662
    <time>   3.54513   6.02290   0.02299   0.01184   0.01186   0.01414
    <time>   3.59005   5.96956   0.05239   0.03131   0.03339   0.11409
    <time>   3.86084   6.15363   0.02294   0.01325   0.01375   0.03052
    <time>   3.61615   6.42196   0.00203   0.00415   0.00507   0.00413
    <time>   3.60794   6.23503   0.02634   0.01088   0.01494   0.03590
    <time>   3.65207   5.95767   0.05993   0.02009   0.02736   0.06209
    <time>   3.52844   5.96569   0.01038   0.04458   0.01207   0.02518
    <time>   3.47280   6.06822   0.02712   0.01699   0.01006   0.03852
    <time>   3.54563   6.17544   0.00633   0.02132   0.00827   0.01098
    <time>   3.48593   6.08244   0.02299   0.05029   0.02920   0.06476
    <time>   3.65566   5.94825   0.04266   0.07974   0.02821   0.07630
    <time>   3.56973   6.08153   0.01148   0.00875   0.00750   0.02182
    <time>   3.58013   5.95234   0.03163   0.01878   0.01484   0.03948
    <time>   3.52974   5.88012   0.02834   0.01291   0.01213   0.01755
    <time>   3.76956   5.99531   0.02397   0.01135   0.01219   0.01445
    <time>   3.64149   5.99532   0.04724   0.02938   0.03349   0.11341
    <time>   3.65184   6.03642   0.02300   0.01295   0.01325   0.03116
    <time>   3.70621   6.13181   0.00200   0.00397   0.00485   0.00396
    <time>   3.48021   6.38780   0.02739   0.01114   0.01524   0.03564
    <time>   3.54207   6.16315   0.07558   0.03094   0.03011   0.06728
    <time>   3.58193   6.09605   0.02676   0.04568   0.02221   0.03079
             DijkOne  AStarOne    ALTOne    DijkBi   AStarBi     ALTBi    s -> t
python stress.py --random-queries 0 --profile --hide-results <  2> /dev/null  289.49s user 0.37s system 96% cpu 5:00.32 total

## WHYS

1. Why in Onedirectional Dijkstra and Onedirectional AStar in certain queries
  vertices are visited many times.
  Bad edge lengths?

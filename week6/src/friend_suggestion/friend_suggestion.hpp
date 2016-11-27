#pragma once

#include <vector>
#include <queue>
#include <limits>
#include <string>

using namespace std;

// External vector of size 2 - for forward and backward search.
// Internal 2-dimensional vector is vector of adjacency lists for each node.
typedef vector<vector<vector<int>>> Adj;

// Distances can grow out of int type
typedef long long Len;

// Vector of two priority queues - for forward and backward searches.
// Each priority queue stores the closest unprocessed node in its head.
typedef vector<priority_queue<pair<Len, int>,
                              vector<pair<Len, int>>,
                              greater<pair<Len, int>>>> Queue;

const Len INFINITY = numeric_limits<Len>::max() / 4;

class Bidijkstra {
    int n_;
    int m_;
    Adj adj_;
    Adj cost_;
    // distance_[0] stores distances for the forward search,
    // and distance_[1] stores distances for the backward search.
    vector<vector<Len>> distance_;
    // Stores all the nodes visited either by forward or backward search.
    vector<int> workset_;
    // Stores a flag for each node which is True iff the node was visited
    // either by forward or backward search.
    vector<bool> visited_;

    vector<vector<int>> parent_;

public:
    Bidijkstra(int n, int m, Adj adj, Adj cost);
    void saveToFile(string filename);
    void clear();
    void visit(Queue& front, int side, int v, Len dist);
    void backtrack(int source, int target);
    Len query(int source, int target);
};

Bidijkstra generateStraight(int numVertices, int edgeCost);
Bidijkstra generateDual(int numVertices1, int edgeCost1, int numVertices2, int edgeCost2);
Bidijkstra generateUnconnected(int numVertices);


Bidijkstra readFromFile(FILE *file);
void processFile(FILE *file, Bidijkstra& bidij);

#include <cstdio>
#include <cassert>
#include <vector>
#include <queue>
#include <limits>
#include <utility>
#include <iostream>

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

ostream& operator<<(ostream& os, const pair<Len, int> p) {
    os << "(len=" << p.first << ",node=" << p.second << ")";
    return os;
}

class Bidijkstra {
    // Number of nodes
    int n_;
    // Graph adj_[0] and cost_[0] correspond to the initial graph,
    // adj_[1] and cost_[1] correspond to the reversed graph.
    // Graphs are stored as vectors of adjacency lists corresponding
    // to nodes.
    // Adjacency list itself is stored in adj_, and the corresponding
    // edge costs are stored in cost_.
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
    Bidijkstra(int n, Adj adj, Adj cost)
        : n_(n),
          adj_(adj),
          cost_(cost),
          distance_(2, vector<Len>(n, INFINITY)),
          parent_(2, vector<int>(n, -1)),
          visited_(n)
    {
        workset_.reserve(n);
    }

    // Initialize the data structures before new query,
    // clear the changes made by the previous query.
    void clear() {

        for (int i = 0; i < workset_.size(); ++i) {
            int v = workset_[i];
            distance_[0][v] = distance_[1][v] = INFINITY;
            visited_[v] = false;
        }
        workset_.clear();
    }

    // Processes visit of either forward or backward search
    // (determined by value of side), to node v trying to
    // relax the current distance by dist.
    void visit(Queue& front, int side, int v, Len dist) {
        // Implement this method yourself
    }

    void backtrack(int source, int target) {
        int current = target;
        cout << "THE PATH" << endl;
        while (current != source) {
            cout << current << " <- ";
            current = parent_[0][current];
        }
        cout << source << endl;
    }

    // Returns the distance from s to t in the graph.
    Len query(int source, int target) {
        clear();
        Queue front(2);
        distance_[0][source] = 0;

        front[0].push(pair<Len, int>(0, source));

        while (!front[0].empty()) {
            pair<Len, int> node = front[0].top();
            front[0].pop();

            //auto node = front[0].pop();
            // cout << "<<< another node " << node << endl;
            visited_[node.second] = true;
            workset_.push_back(node.second);

            if (node.second == target) {
                // cout << "reached target " << target << endl;
                break;
            }

            //for (int neighbor : adj_[0][node.second]) {
            auto neighbors = adj_[0][node.second];
            for (int neighbor_index = 0; neighbor_index < neighbors.size(); neighbor_index++) {
                int neighbor = neighbors[neighbor_index];

                if (visited_[neighbor]) {
                    continue;
                }
                int alt = distance_[0][node.second] + cost_[0][node.second][neighbor_index];
                // cout << "neighbor_index " << neighbor_index << " is " << neighbor << " alt " << alt << endl;
                // cout << "dist to node " << node.second
                //     << " = " << distance_[0][node.second] << endl;
                // cout << "cost from " << node.second
                //     << " to " << neighbor
                //     << " = " << cost_[0][node.second][neighbor] << endl;

                front[0].push(pair<Len, int>(alt, neighbor));

                if (alt < distance_[0][neighbor]) {
                    distance_[0][neighbor] = alt;
                    parent_[0][neighbor] = node.second;
                }
            }
        }

        //visit(front, 0, source, 0);
        //visit(front, 1, target, 0);
        // Implement the rest of the algorithm yourself

        if (distance_[0][target] == INFINITY) {
            return -1;
        }
        // backtrack(source, target);
        return distance_[0][target];
        //return -1;
    }
};

Bidijkstra readFromStdin() {
    int n, m;
    scanf("%d%d", &n, &m);
    Adj adj(2, vector<vector<int>>(n));
    Adj cost(2, vector<vector<int>>(n));
    for (int i=0; i<m; ++i) {
        int u, v, c;
        scanf("%d%d%d", &u, &v, &c);
        adj[0][u-1].push_back(v-1);
        cost[0][u-1].push_back(c);
        adj[1][v-1].push_back(u-1);
        cost[1][v-1].push_back(c);
    }
    return Bidijkstra(n, adj, cost);
}

void processStdin(Bidijkstra& bidij) {
    int t;
    scanf("%d", &t);
    for (int i=0; i<t; ++i) {
        int u, v;
        scanf("%d%d", &u, &v);
        //printf("incoming query #%d, (%d,%d)\n", i, u-1, v-1);
        int result = bidij.query(u-1, v-1);
        printf("%d\n", result);
        // printf("query result #%d (%d,%d), %lld\n", i, u-1, v-1, result);
        // printf("------------------\n");
    }
}

int main() {
    Bidijkstra bidij = readFromStdin();
    processStdin(bidij);
}

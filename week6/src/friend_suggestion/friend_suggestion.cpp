#include <cstdio>
#include <cassert>
#include <vector>
#include <queue>
#include <stack>
#include <limits>
#include <utility>
#include <iostream>
#include <fstream>

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
    int m_;
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
    Bidijkstra(int n, int m, Adj adj, Adj cost)
        : n_(n),
          m_(m),
          adj_(adj),
          cost_(cost),
          distance_(2, vector<Len>(n, INFINITY)),
          parent_(2, vector<int>(n, -1)),
          visited_(n)
    {
        workset_.reserve(n);
    }

    __attribute_used__
    int saveToFile(string filename) {
        ofstream file(filename);
        if (!file.is_open()) {
            return 0;
        }

        file << n_ << " " << m_ << endl;
        for (int from = 0; from < adj_[0].size(); from++) {
            for (int i = 0; i < adj_[0][from].size(); i++) {
                int to = adj_[0][from][i];
                file << from+1 << " " << to+1 << " " << cost_[0][from][i] << endl;
            }
        }
        file.close();
        return 0;
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
        stack<int> path;

        int current = target;
        // cout << "THE PATH" << endl;
        while (current != source) {
            //cerr << current + 1 << " ";
            path.push(current);
            current = parent_[0][current];
        }
        path.push(source);

        while (!path.empty()) {
            cerr << path.top() + 1 << " ";
            path.pop();
        }
        cerr << endl;
        //cerr << source + 1 << endl;
    }

    // Returns the distance from s to t in the graph.
    Len query(int source, int target) {
        clear();
        Queue front(2);
        distance_[0][source] = 0;

        front[0].push({0, source});

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

                //front[0].push(pair<Len, int>(alt, neighbor));
                front[0].push({alt, neighbor});

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
        #ifdef MAIN
        backtrack(source, target);
        #endif // MAIN
        return distance_[0][target];
        //return -1;
    }
};

Bidijkstra generateUnconnected(int numVertices) {
    Adj adj(2, vector<vector<int>>(numVertices));
    Adj cost(2, vector<vector<int>>(numVertices));
    Bidijkstra result = Bidijkstra(numVertices, 0, adj, cost);
    return result;
}

Bidijkstra generateStraight(int numVertices, int edgeCost) {
    Adj adj(2, vector<vector<int>>(numVertices));
    Adj cost(2, vector<vector<int>>(numVertices));
    for (int i = 0; i < numVertices - 1; ++i) {
        adj[0][i].push_back(i+1);
        cost[0][i].push_back(edgeCost);
        adj[1][i].push_back(i+1);
        cost[1][i].push_back(edgeCost);
    }
    Bidijkstra result = Bidijkstra(numVertices, numVertices - 1, adj, cost);
    //result.saveToFile("dummy.txt");
    return result;
}

Bidijkstra generateDual(int numVertices1, int edgeCost1, int numVertices2, int edgeCost2) {
    int n = numVertices1 + numVertices2;
    int m = n;

    Adj adj(2, vector<vector<int>>(n));
    Adj cost(2, vector<vector<int>>(n));

    auto add = [&adj, &cost](int from, int to, int edgeCost) {
        adj[0][from].push_back(to);
        cost[0][from].push_back(edgeCost);
        adj[1][from].push_back(to);
        cost[1][from].push_back(edgeCost);
    };

    for (int i = 0; i < numVertices1 - 1; ++i) {
        add(i, i+1, edgeCost1);
    }
    add(0, numVertices1, edgeCost2);
    for (int i = numVertices1; i < numVertices1 + numVertices2 - 1; ++i) {
        add(i, i+1, edgeCost2);
    }
    add(numVertices1 + numVertices2 - 1, numVertices1-1, edgeCost2);

    Bidijkstra result = Bidijkstra(n, m, adj, cost);
    //result.saveToFile("dummy.txt");
    return result;
}

//void dummy() {
//    Adj adj(2, vector<vector<int>>(0));
//    Adj cost(2, vector<vector<int>>(0));
//    Bidijkstra temp(0, 0, adj, cost);
//    temp.saveToFile("/dev/null");
//}

Bidijkstra readFromFile(FILE *file) {
    int n, m;
    fscanf(file, "%d%d", &n, &m);
    Adj adj(2, vector<vector<int>>(n));
    Adj cost(2, vector<vector<int>>(n));
    for (int i=0; i<m; ++i) {
        int u, v, c;
        fscanf(file, "%d%d%d", &u, &v, &c);
        adj[0][u-1].push_back(v-1);
        cost[0][u-1].push_back(c);
        adj[1][v-1].push_back(u-1);
        cost[1][v-1].push_back(c);
    }
    return Bidijkstra(n, m, adj, cost);
}

void processFile(FILE *file, Bidijkstra& bidij) {
    int t;
    fscanf(file, "%d", &t);
    for (int i=0; i<t; ++i) {
        int u, v;
        fscanf(file, "%d%d", &u, &v);
        //printf("incoming query #%d, (%d,%d)\n", i, u-1, v-1);
        int result = bidij.query(u-1, v-1);
        printf("%d\n", result);
        // printf("query result #%d (%d,%d), %lld\n", i, u-1, v-1, result);
        // printf("------------------\n");
    }
}

#ifdef MAIN
int main() {
    Bidijkstra bidij = readFromFile(stdin);
    processFile(stdin, bidij);
    //bidij.saveToFile("saved.txt");
}
#endif // MAIN

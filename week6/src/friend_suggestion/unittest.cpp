#include "friend_suggestion.hpp"

#include <iostream>
#include <fstream>
#include <sstream>
#include <glob.h>

#ifdef TEST

#define CATCH_CONFIG_MAIN
#include "catch.hpp"

//namespace fs = std::experimental::filesystem;

TEST_CASE("Generated straight", "[straight]") {
    //REQUIRE(1 == 1);
    SECTION("10, 10") {
        Bidijkstra generated = generateStraight(10, 10);
        int result = generated.query(0, 9);
        REQUIRE(90 == result);
    }

    SECTION("1 000 000, 1000") {
        Bidijkstra generated = generateStraight(1'000'000, 1000);
        int result = generated.query(0, 1'000'000-1);
        REQUIRE(1'000'000*1000 - 1000 == result);
    }

}

TEST_CASE("Generated dual", "[dual]") {
    //REQUIRE(1 == 1);
    SECTION("3 1, 3 2") {
        Bidijkstra generated = generateDual(3, 1, 3, 2);
        generated.saveToFile("dual.in");

        REQUIRE(2 == generated.query(0, 2));
        REQUIRE(6 == generated.query(0, 5));
        REQUIRE(2 == generated.query(0, 2));
        REQUIRE(6 == generated.query(0, 5));
    }
}

TEST_CASE("Unconnected", "[unconnected]") {
    //REQUIRE(1 == 1);
    SECTION("unconnected") {
        Bidijkstra generated = generateUnconnected(10);

        REQUIRE(-1 == generated.query(0, 1));
        REQUIRE(-1 == generated.query(0, 2));
        REQUIRE(-1 == generated.query(0, 3));

        REQUIRE(-1 == generated.query(0, 1));
    }
}


string slurp(string filename) {
    ifstream expected_file(filename);
    stringstream expected;
    expected << expected_file.rdbuf();
    return expected.str();
}


string runAndReturn(auto reader, string inFilename) {
    FILE *file = fopen(inFilename.c_str(), "rt");
    Bidijkstra* graph = reader(file);
    ostringstream output;
    processFile(file, *graph, output);
    delete graph;
    fclose(file);
    return output.str();
}


TEST_CASE("Manual", "[manual]") {
    SECTION("manual") {
        vector<vector<string>> tests = {
            {"./test_small/small1.in", "./test_small/small1.out"},
            {"./test_small/small2.in", "./test_small/small2.out"},
            {"./test_small/small3.in", "./test_small/small3.out"},
            {"./test_small/case2-1.in", "./test_small/case2-1.out"},
            {"./test_small/case2-2.in", "./test_small/case2-2.out"},
            {"./test_small/case2-3.in", "./test_small/case2-3.out"},
            {"./test_small/case2.in", "./test_small/case2.out"}
        };

       for (auto test : tests) {
           cout << "TEST IN " << test[0] << " OUT " << test[1] << endl;
           string actual = runAndReturn(readFromFile, test[0]);
           REQUIRE(slurp(test[1]) == actual);
       }

        // glob_t glob_result;
        // glob("tests#<{(|.in", GLOB_TILDE, NULL, &glob_result);
        //
        // for (unsigned int i = 0; i < glob_result.gl_pathc; ++i) {
        //     cout << "TEST: " << glob_result.gl_pathv[i] << endl;
        //     FILE *file = fopen(glob_result.gl_pathv[i], "r");
        //     Bidijkstra graph = readFromFile(file);
        //     processFile(file, graph);
        //     fclose(file);
        // }

//        for (auto &p : fs::directory_iterator("tests")) {
//            cout << p << endl;
//        }

    }
}

string toHex(const string& s, bool upper_case /* = true */)
{
    ostringstream ret;

    for (string::size_type i = 0; i < s.length(); ++i)
        ret << std::hex << std::setfill('0') << std::setw(2) << (upper_case ? std::uppercase : std::nouppercase) << (int)s[i];

    return ret.str();
}

TEST_CASE("AStar", "[astar]") {
    SECTION("astar") {
        vector<vector<string>> tests = {
            {"./test_astar/sample1.in", "./test_astar/sample1.out"},
            {"./test_astar/sample2.in", "./test_astar/sample2.out"},
            {"./test_astar/case1.in", "./test_astar/case1.out"},
            {"./test_astar/case2.in", "./test_astar/case2.out"},
            {"./test_astar/case3.in", "./test_astar/case3.out"},
            {"./test_astar/case3.limited.in", "./test_astar/case3.limited.out"},
            {"./test_astar/gen10.in", "./test_astar/gen10.out"},
            {"./test_astar/gen100.in", "./test_astar/gen100.out"},
            {"./test_astar/gen1000.in", "./test_astar/gen1000.out"},
        };

       for (auto test : tests) {
           cout << "TEST IN " << test[0] << " OUT " << test[1] << endl;
           string actual = runAndReturn(readFromFileWithDistance, test[0]);
           // cout << "A>" << toHex(actual, true) << "<" << endl;
           // cout << "E>" << toHex(slurp(test[1]), true) << "<" << endl;
           REQUIRE(slurp(test[1]) == actual);
       }
    }
}

TEST_CASE("Single", "[single]") {
    SECTION("single") {
        vector<vector<string>> tests = {
            //{"./test_astar/sample2.in", "./test_astar/sample2.out"},
            {"./test_astar/case2.in", "./test_astar/case2.out"},
        };

       for (auto test : tests) {
           cout << "TEST IN " << test[0] << " OUT " << test[1] << endl;
           string actual = runAndReturn(readFromFileWithDistance, test[0]);
           REQUIRE(slurp(test[1]) == actual);
       }
    }
}

#endif // TEST

#include "friend_suggestion.hpp"

#include <iostream>
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

TEST_CASE("Manual", "[manual]") {
    //REQUIRE(1 == 1);
    SECTION("manual") {
        //Bidijkstra generated = generateUnconnected(10);
        glob_t glob_result;
        glob("tests/*.in", GLOB_TILDE, NULL, &glob_result);

        for (unsigned int i = 0; i < glob_result.gl_pathc; ++i) {
            cout << "TEST: " << glob_result.gl_pathv[i] << endl;
            FILE *file = fopen(glob_result.gl_pathv[i], "r");
            Bidijkstra graph = readFromFile(file);
            processFile(file, graph);
            fclose(file);
        }

//        for (auto &p : fs::directory_iterator("tests")) {
//            cout << p << endl;
//        }

    }
}

#endif // TEST

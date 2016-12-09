CC = g++
CXXFLAGS = -rdynamic -g -ggdb -O0 -pipe -std=c++14 -Wall
LIBS = -lm -lSegFault
INCLUDES = -I.
WORKDIR =
#bin/unittest

MAIN = friend_suggestion
TEST = unittest

$(MAIN): CXXFLAGS += -DMAIN
$(MAIN): $(eval WORKDIR=bin/friend_suggestion)
#$(MAIN): WORKDIR += bin/friend_suggestion

$(TEST): CXXFLAGS += -DTEST
$(TEST): $(eval WORKDIR=bin/unittest)
#$(TEST): WORKDIR += bin/unittest

MAIN_SRCS = friend_suggestion.cpp
MAIN_OBJS = $(addprefix $(WORKDIR)/, $(MAIN_SRCS:.cpp=.o))
TEST_SRCS = friend_suggestion.cpp unittest.cpp
#TEST_OBJS = $(TEST_SRCS:%.cpp=$(WORKDIR)/%.o)
TEST_OBJS = $(addprefix $(WORKDIR)/, $(TEST_SRCS:.cpp=.o))
#TEST_OBJS = $(TEST_SRCS:.cpp=.o)


all: $(TEST) $(MAIN)
	@echo $(TEST_OBJS) $(MAIN_OBJS)

$(TEST): $(TEST_OBJS)
	@echo "Workdir = $(WORKDIR)"
	$(CC) $(CXXFLAGS) $(INCLUDES) -o $(TEST) $(TEST_OBJS) $(LIBS)

$(MAIN): $(MAIN_OBJS)
	@echo "Workdir = $(WORKDIR)"
	$(CC) $(CXXFLAGS) $(INCLUDES) -o $(MAIN) $(MAIN_OBJS) $(LIBS)

$(TEST_OBJS): $(WORKDIR)/%.o : %.cpp
	$(CC) $(CXXFLAGS) $(INCLUDES) -c $< -o $@

$(MAIN_OBJS): $(WORKDIR)/%.o : %.cpp
	$(CC) $(CXXFLAGS) $(INCLUDES) -c $< -o $@

clean:
	$(RM) $(MAIN_OBJS) $(TEST_OBJS) $(MAIN) $(TEST) *~

#.cpp.o:
#	$(CC) $(CXXFLAGS) $(INCLUDES) -c $< -o $@

#         MAIN_SRCS = friend_suggestion.cpp
#         MAIN_OBJS = $(addprefix $(WORKDIR)/, $(MAIN_SRCS:.cpp=.o))
#         TEST_SRCS = friend_suggestion.cpp unittest.cpp
#         TEST_OBJS = $(TEST_SRCS:%.cpp=$(WORKDIR)/%.o)
#         #TEST_OBJS = $(addprefix $(WORKDIR)/, $(TEST_SRCS:.cpp=.o))
#         #TEST_OBJS = $(TEST_SRCS:.cpp=.o)
#         
#         TARGET_TEST = $(addprefix $(WORKDIR)/, $(TEST))
#         
#         .PHONY: depend clean
#         
#         #all:	$(MAIN) $(TEST)
#         all: $(TARGET_TEST)
#         #	@echo Main
#         
#         $(TARGET_TEST): $(addprefix $(WORKDIR)/, $(TEST_OBJS))
#         	$(CC) $(CXXFLAGS) $(INCLUDES) -c $< -o $@
#         
#         $(MAIN): $(MAIN_OBJS)
#         	$(CC) $(CXXFLAGS) $(INCLUDES) -o $(MAIN) $(MAIN_OBJS) $(LIBS)
#         
#         #$(TEST): $(addprefix $(WORKDIR)/, $(TEST_OBJS))
#         $(TEST): $(TEST_OBJS)
#         	@echo "Workdir = $(WORKDIR)"
#         	$(CC) $(CXXFLAGS) $(INCLUDES) -o $(TEST) $(TEST_OBJS) $(LIBS)
#         
#         #$(WORKDIR)/.cpp.o:
#         #.cpp.o:
#         $(TEST_OBJS): $(WORKDIR)/%.o : %.cpp
#         	$(CC) $(CXXFLAGS) $(INCLUDES) -c $< -o $@
#         
#         clean:
#         	$(RM) $(MAIN_OBJS) $(TEST_OBJS) *~ $(MAIN) $(TEST)
#         
#         depend: $(MAIN_SRCS) $(TEST_SRCS)
#         	makedepend $(INCLUDES) $^
#         
#         
#         #all:
#         #	g++ $(CXXFLAGS) friend_suggestion.cpp -o friend_suggestion $(LIBS)
#         
#         
#         #test:
#         #	g++ $(CXXFLAGS) unittest.cpp -o unittest $(LIBS)
#         # DO NOT DELETE

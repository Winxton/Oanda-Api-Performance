CXX = g++
CXXFLAGS = -Wall -W -lPocoNetSSL -lPocoNet -std=c++0x -pedantic \

EXEC = perfcpp
OBJECTS = apiperf.o cJSON.o

${EXEC}: ${OBJECTS}
	${CXX} ${OBJECTS} ${CXXFLAGS} -o ${EXEC}

apiperf.o: apiperf.cpp

clean:
	rm ${OBJECTS} ${EXEC}

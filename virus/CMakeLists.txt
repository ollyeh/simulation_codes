cmake_minimum_required(VERSION 3.31)
project(virus)

set(CMAKE_CXX_STANDARD 20)
add_executable(virus main.cpp)

find_package(OpenMP)
target_link_libraries(virus PUBLIC OpenMP::OpenMP_CXX)

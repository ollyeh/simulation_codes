cmake_minimum_required(VERSION 3.31)
project(virus)

set(CMAKE_CXX_STANDARD 20)
add_executable(virus main.cpp)

find_package(OpenMP)
if(OpenMP_CXX_FOUND)
    target_link_libraries(virus PRIVATE OpenMP::OpenMP_CXX)
endif()

find_package(nlohmann_json REQUIRED)
target_link_libraries(virus PRIVATE nlohmann_json::nlohmann_json)

find_package(OpenCV)
target_include_directories(virus PUBLIC ${OpenCV_INCLUDE_DIRS})
target_link_libraries(virus PUBLIC ${OpenCV_LIBS})
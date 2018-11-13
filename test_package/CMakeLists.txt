cmake_minimum_required(VERSION 3.1.2)
project(test_package CXX)

set(CMAKE_VERBOSE_MAKEFILE TRUE)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

find_package(GTest REQUIRED)
if (NOT GTEST_FOUND)
    message(FATAL_ERROR "Could not find GTest")
endif()

if(WITH_GMOCK)
    find_package(GMock REQUIRED)
    if (NOT GMOCK_FOUND)
        message(FATAL_ERROR "Could not find GMock")
    endif()
endif()

if(WITH_MAIN)
    add_executable(${PROJECT_NAME} test_package.cpp)
else()
    add_executable(${PROJECT_NAME} main.cpp test_package.cpp)
endif()

target_link_libraries(${PROJECT_NAME} ${CONAN_LIBS})
set_property(TARGET ${PROJECT_NAME} PROPERTY CXX_STANDARD 11)
if(WITH_GMOCK)
    target_compile_definitions(${PROJECT_NAME} PRIVATE WITH_GMOCK)
endif()

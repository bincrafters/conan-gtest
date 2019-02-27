cmake_minimum_required(VERSION 2.8.11)
project(cmake_wrapper)

include("${CMAKE_BINARY_DIR}/conanbuildinfo.cmake")
conan_basic_setup()

option(GTEST_NO_MAIN "Generate google main libraries" OFF)

if(MSVC)
  if(MSVC_VERSION AND MSVC_VERSION GREATER_EQUAL 1910)
    add_definitions(-DGTEST_LANG_CXX11=1 -DGTEST_HAS_TR1_TUPLE=0)
  endif(MSVC_VERSION AND MSVC_VERSION GREATER_EQUAL 1910)
endif(MSVC)

add_subdirectory("source_subfolder")

configure_file("${PROJECT_SOURCE_DIR}/FindGMock.cmake.in" "${PROJECT_BINARY_DIR}/FindGMock.cmake" @ONLY)
configure_file("${PROJECT_SOURCE_DIR}/FindGTest.cmake.in" "${PROJECT_BINARY_DIR}/FindGTest.cmake" @ONLY)

install(FILES FindGTest.cmake DESTINATION ${CMAKE_INSTALL_PREFIX})
if (BUILD_GMOCK)
  install(FILES FindGMock.cmake DESTINATION ${CMAKE_INSTALL_PREFIX})
endif()

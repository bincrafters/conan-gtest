find_path(
  GTEST_INCLUDE_DIRS
  NAMES
  gtest
  PATHS
  include)

find_library(
  GTEST_LIBRARIES
  NAMES
  gtest
  libgtest
  PATHS
  lib)

find_library(
  GTEST_MAIN_LIBRARIES
  NAMES
  gtest_main
  libgtest_main
  PATHS
  lib)

SET(GTEST_BOTH_LIBRARIES ${GTEST_MAIN_LIBRARIES} ${GTEST_LIBRARIES})

include(FindPackageHandleStandardArgs)

find_package_handle_standard_args(GTEST REQUIRED_VARS GTEST_LIBRARIES GTEST_MAIN_LIBRARIES GTEST_BOTH_LIBRARIES GTEST_INCLUDE_DIRS)

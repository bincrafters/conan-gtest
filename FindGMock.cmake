find_path(
  GMOCK_INCLUDE_DIR
  NAMES
  gmock
  PATHS
  include)

find_path(
  GTEST_INCLUDE_DIR
  NAMES
  gtest
  PATHS
  include)

SET(GMOCK_INCLUDE_DIRS ${GMOCK_INCLUDE_DIR} ${GTEST_INCLUDE_DIR})

find_library(
  GTEST_LIBRARY
  NAMES
  gtest
  libgtest
  PATHS
  lib
  )

find_library(
  GMOCK_LIBRARY
  NAMES
  gmock
  libgmock
  PATHS
  lib)

find_library(
  GMOCK_MAIN_LIBRARIES
  NAMES
  gmock_main
  libgmock_main
  PATHS
  lib)

SET(GMOCK_LIBRARIES ${GMOCK_LIBRARY} ${GTEST_LIBRARY})

SET(GMOCK_BOTH_LIBRARIES ${GMOCK_MAIN_LIBRARIES} ${GMOCK_LIBRARIES})

include(FindPackageHandleStandardArgs)

find_package_handle_standard_args(GTEST REQUIRED_VARS GMOCK_INCLUDE_DIR GTEST_INCLUDE_DIR GMOCK_INCLUDE_DIRS GTEST_LIBRARY GMOCK_LIBRARY GMOCK_LIBRARIES GMOCK_MAIN_LIBRARIES GMOCK_BOTH_LIBARIES)

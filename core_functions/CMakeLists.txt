cmake_minimum_required(VERSION 3.5...3.29)

project(CoreFunctionsExtension)

include_directories(include)
add_subdirectory(aggregate)
add_subdirectory(scalar)

add_library_unity(
  duckdb_core_functions_main
  OBJECT
  core_functions_extension.cpp
  function_list.cpp
  lambda_functions.cpp)

set(CORE_FUNCTION_FILES
    ${CORE_FUNCTION_FILES}
    $<TARGET_OBJECTS:duckdb_core_functions_main>)

# When this project is embedded into the main DuckDB build we link these
# object files directly into the core library.
set(ALL_OBJECT_FILES
    ${ALL_OBJECT_FILES}
    ${CORE_FUNCTION_FILES}
    PARENT_SCOPE)

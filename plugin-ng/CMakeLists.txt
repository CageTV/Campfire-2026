cmake_minimum_required(VERSION 3.21)

# Campfire.dll built against alandtse's CommonLibSSE-NG (the "ng" branch of alandtse/CommonLibVR), which knows Skyrim 1.7.x. The sources are the
# ones in ../plugin; only the library and how it is found differ from ../plugin/CMakeLists.txt (which uses CharmedBaryon's 3.7.0 from vcpkg).
project(Campfire VERSION 1.0.2 LANGUAGES CXX)

set(COMMONLIB_DIR "E:/WorkSpace/CommonLibSSE-NG-alandtse" CACHE PATH "alandtse CommonLibSSE-NG checkout (branch ng)")
set(ENABLE_SKYRIM_VR OFF CACHE BOOL "" FORCE)  # Campfire.dll is for Special / Anniversary Edition
set(BUILD_TESTS OFF CACHE BOOL "" FORCE)
add_subdirectory("${COMMONLIB_DIR}" CommonLibSSE EXCLUDE_FROM_ALL)
include("${COMMONLIB_DIR}/cmake/CommonLibSSE.cmake")  # add_commonlibsse_plugin()

set(SRC "${CMAKE_CURRENT_SOURCE_DIR}/../plugin")
add_commonlibsse_plugin(${PROJECT_NAME} NAME "Campfire" AUTHOR "CageTV" SOURCES
    ${SRC}/src/main.cpp
    ${SRC}/src/Menu.cpp
    ${SRC}/src/NativeMcm.cpp
    ${SRC}/src/Hotkeys.cpp
    ${SRC}/src/Ids.cpp
    ${SRC}/src/CutUp.cpp
)

target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_23)
target_include_directories(${PROJECT_NAME} PRIVATE ${SRC}/src ${SRC}/include)
target_precompile_headers(${PROJECT_NAME} PRIVATE ${SRC}/src/PCH.h)
target_compile_options(${PROJECT_NAME} PRIVATE $<$<CONFIG:Release>:/Z7>)
target_link_options(${PROJECT_NAME} PRIVATE $<$<CONFIG:Release>:/DEBUG /OPT:REF /OPT:ICF>)

# local extra targets for the same library build (Frostfall, Last Seed); not part of this repository
include("${CMAKE_CURRENT_SOURCE_DIR}/extras.cmake" OPTIONAL)

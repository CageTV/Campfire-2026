cmake_minimum_required(VERSION 3.21)

# Campfire.dll - the SKSE plugin behind Campfire 2026's SKSE Menu Framework settings pages.
project(Campfire VERSION 1.0.0 LANGUAGES CXX)

find_package(CommonLibSSE CONFIG REQUIRED)

add_commonlibsse_plugin(${PROJECT_NAME} NAME "Campfire" AUTHOR "CageTV" SOURCES
    src/main.cpp
    src/Menu.cpp
    src/NativeMcm.cpp
    src/Hotkeys.cpp
    src/Ids.cpp
)

target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_23)
target_include_directories(${PROJECT_NAME} PRIVATE src include)
target_precompile_headers(${PROJECT_NAME} PRIVATE src/PCH.h)
target_compile_options(${PROJECT_NAME} PRIVATE $<$<CONFIG:Release>:/Z7>)
target_link_options(${PROJECT_NAME} PRIVATE $<$<CONFIG:Release>:/DEBUG /OPT:REF /OPT:ICF>)

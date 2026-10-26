# Frostfall and Last Seed built against the same alandtse CommonLibSSE-NG, for the Skyrim 1.7.104 test list. Output: build/release/out/<target>/<name>.dll
function(ng_plugin TARGET NAME VERSION ROOT)
    set(SRCS ${ARGN})
    list(TRANSFORM SRCS PREPEND "${ROOT}/src/")
    add_commonlibsse_plugin(${TARGET} NAME "${NAME}" AUTHOR "CageTV" VERSION ${VERSION} SOURCES ${SRCS})
    target_compile_features(${TARGET} PRIVATE cxx_std_23)
    target_include_directories(${TARGET} PRIVATE ${ROOT}/src ${ROOT}/include)
    target_precompile_headers(${TARGET} PRIVATE ${ROOT}/src/PCH.h)
    target_compile_options(${TARGET} PRIVATE $<$<CONFIG:Release>:/Z7>)
    target_link_options(${TARGET} PRIVATE $<$<CONFIG:Release>:/DEBUG /OPT:REF /OPT:ICF>)
    set_target_properties(${TARGET} PROPERTIES OUTPUT_NAME "${NAME}" RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/out/${TARGET}"
                          ARCHIVE_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/out/${TARGET}" PDB_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/out/${TARGET}"
                          LIBRARY_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/out/${TARGET}")
endfunction()

set(FF "E:/WorkSpace/Frostfall-2026-repo/plugin")
set(FF_SRC main.cpp Settings.cpp Game.cpp Hud.cpp Menu.cpp NativeMcm.cpp Hotkeys.cpp)
ng_plugin(FrostfallRegular Frostfall 4.1.0 "${FF}" ${FF_SRC})
ng_plugin(FrostfallESL Frostfall 4.1.0 "${FF}" ${FF_SRC})
target_compile_definitions(FrostfallESL PRIVATE FROSTFALL_ESL)

set(LS "E:/WorkSpace/Last-Seed-2026/plugin")
ng_plugin(LastSeed LastSeed 1.0.0 "${LS}" main.cpp Settings.cpp Game.cpp Hud.cpp Menu.cpp AutoStart.cpp Spoilage.cpp Freshness.cpp GridInv.cpp NativeMcm.cpp
          Hotkeys.cpp NativeFoodLists.cpp Compat.cpp Ids.cpp)

# Preditor Flee Fire (CageTV/Preiditor-flee): flat layout, sources and include/ at the repository root
set(PF "E:/WorkSpace/Preiditor-flee")
add_commonlibsse_plugin(PreditorFleeFire NAME "Preditor Flee Fire" AUTHOR "CageTV" VERSION 1.0.0 SOURCES
    ${PF}/main.cpp ${PF}/Settings.cpp ${PF}/Events.cpp ${PF}/Menu.cpp)
target_compile_features(PreditorFleeFire PRIVATE cxx_std_23)
target_include_directories(PreditorFleeFire PRIVATE ${PF} ${PF}/include)
target_compile_options(PreditorFleeFire PRIVATE /Zc:preprocessor $<$<CONFIG:Release>:/Z7>)
target_compile_definitions(PreditorFleeFire PRIVATE UNICODE _UNICODE)
target_precompile_headers(PreditorFleeFire PRIVATE ${PF}/include/PCH.h)
target_link_options(PreditorFleeFire PRIVATE $<$<CONFIG:Release>:/DEBUG /OPT:REF /OPT:ICF>)
set_target_properties(PreditorFleeFire PROPERTIES RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/out/PreditorFleeFire"
                      ARCHIVE_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/out/PreditorFleeFire" PDB_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/out/PreditorFleeFire")

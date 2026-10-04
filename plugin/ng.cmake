# Campfire.dll on alandtse's CommonLibSSE-NG; included by E:/WorkSpace/ng-build/CMakeLists.txt (see ng_plugin there)
ng_plugin(TARGET Campfire NAME Campfire VERSION 1.0.2 ROOT "${CMAKE_CURRENT_LIST_DIR}"
    SOURCES src/main.cpp src/Menu.cpp src/NativeMcm.cpp src/Hotkeys.cpp src/Ids.cpp
    INCLUDES "${CMAKE_CURRENT_LIST_DIR}/src" "${CMAKE_CURRENT_LIST_DIR}/include"
    PCH "${CMAKE_CURRENT_LIST_DIR}/src/PCH.h")

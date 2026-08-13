file( READ "${SOURCE_DIR}/CMakeLists.txt" content )
string( REPLACE "CMAKE_POLICY(SET CMP0026 OLD)" "CMAKE_POLICY(SET CMP0026 NEW)" content "${content}" )
file( WRITE "${SOURCE_DIR}/CMakeLists.txt" "${content}" )

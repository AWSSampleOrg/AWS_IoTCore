file(GLOB SRC_FILES
       "*.cpp"
)

add_executable(${PROJECT_NAME} ${SRC_FILES})

set_target_properties(${PROJECT_NAME} PROPERTIES
    CXX_STANDARD 14)

#set warnings
if (MSVC)
    target_compile_options(${PROJECT_NAME} PRIVATE /W4 /WX /wd4068)
else ()
    target_compile_options(${PROJECT_NAME} PRIVATE -Wall -Wno-long-long -pedantic -Werror)
endif ()

find_package(aws-crt-cpp REQUIRED)

target_link_libraries(${PROJECT_NAME} AWS::aws-crt-cpp)

# Copy certificates files
set(TARGET_CERTIFICATES_DIR $<TARGET_FILE_DIR:${PROJECT_NAME}>/certificates)
add_custom_command(
    TARGET ${PROJECT_NAME}
    POST_BUILD
    COMMAND ${CMAKE_COMMAND} -E make_directory ${TARGET_CERTIFICATES_DIR}
    COMMAND ${CMAKE_COMMAND} -E copy ${CMAKE_CURRENT_SOURCE_DIR}/certificates/AmazonRootCA1.pem ${TARGET_CERTIFICATES_DIR}
    COMMAND ${CMAKE_COMMAND} -E copy ${CMAKE_CURRENT_SOURCE_DIR}/certificates/device_cert_key_filename.key ${TARGET_CERTIFICATES_DIR}
    COMMAND ${CMAKE_COMMAND} -E copy ${CMAKE_CURRENT_SOURCE_DIR}/certificates/device_cert_filename.pem ${TARGET_CERTIFICATES_DIR}
    COMMENT "Post Event"
)

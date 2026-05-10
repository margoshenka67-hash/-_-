cmake_minimum_required(VERSION 3.10)

project(Lab6_OpenCV)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

find_package(OpenCV REQUIRED)

include_directories(include)
include_directories(${OpenCV_INCLUDE_DIRS})

add_executable(Lab6
    src/main.cpp
    src/CameraProvider.cpp
    src/KeyProcessor.cpp
    src/FrameProcessor.cpp
    src/Display.cpp
    src/FaceDetector.cpp
)

target_link_libraries(Lab6 ${OpenCV_LIBS})

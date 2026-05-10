#include "CameraProvider.hpp"
#include <iostream>
    
CameraProvider::CameraProvider(int cameraIndex) {
    capture.open(cameraIndex);

    if (!capture.isOpened()) {
        std::cerr << "Error: cannot open camera." << std::endl;
    }
}

bool CameraProvider::isOpened() const {
    return capture.isOpened();
}

cv::Mat CameraProvider::getFrame() {
    cv::Mat frame;
    capture >> frame;
    return frame;
}

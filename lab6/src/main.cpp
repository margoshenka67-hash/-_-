#include <opencv2/opencv.hpp>
#include <iostream>
#include <chrono>
#include <string>

#include "CameraProvider.hpp"
#include "KeyProcessor.hpp"
#include "FrameProcessor.hpp"
#include "Display.hpp"

int main() {
    CameraProvider camera(0);

    if (!camera.isOpened()) {
        std::cerr << "Program stopped because camera was not opened." << std::endl;
        return 1;
    }

    KeyProcessor keyProcessor;
    FrameProcessor frameProcessor;
    Display display("Lab 6 OpenCV");

    cv::createTrackbar("Brightness", display.getWindowName(), &FrameProcessor::brightness, 100);
    cv::createTrackbar("Canny threshold", display.getWindowName(), &FrameProcessor::cannyThreshold, 200);

    int frameCounter = 0;
    auto startTime = std::chrono::steady_clock::now();

    while (true) {
        cv::Mat frame = camera.getFrame();

        if (frame.empty()) {
            std::cerr << "Error: empty frame." << std::endl;
            break;
        }

        int key = cv::waitKey(1);

        if (!keyProcessor.processKey(key)) {
            break;
        }

        cv::Mat processedFrame = frameProcessor.process(frame, keyProcessor.getMode());

        frameCounter++;

        auto currentTime = std::chrono::steady_clock::now();
        double seconds = std::chrono::duration<double>(currentTime - startTime).count();
        double fps = frameCounter / seconds;

        std::string modeText = "Mode: " + std::string(keyProcessor.getModeName());
        std::string fpsText = "FPS: " + std::to_string(static_cast<int>(fps));
        std::string helpText = "Keys: 0 normal, 1 invert, 2 gray, 3 blur, 4 canny, 5 sobel, 6 threshold, q exit";

        cv::putText(processedFrame, modeText, cv::Point(20, 30),
                    cv::FONT_HERSHEY_SIMPLEX, 0.8, cv::Scalar(0, 255, 0), 2);

        cv::putText(processedFrame, fpsText, cv::Point(20, 60),
                    cv::FONT_HERSHEY_SIMPLEX, 0.8, cv::Scalar(0, 255, 0), 2);

        cv::putText(processedFrame, helpText, cv::Point(20, processedFrame.rows - 20),
                    cv::FONT_HERSHEY_SIMPLEX, 0.5, cv::Scalar(0, 255, 0), 1);

        display.show(processedFrame);
    }

    cv::destroyAllWindows();

    return 0;
}

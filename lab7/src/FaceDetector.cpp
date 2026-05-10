#include "FaceDetector.hpp"
#include <iostream>
#include <chrono>

FaceDetector::FaceDetector() {
    net = cv::dnn::readNetFromCaffe(
        "deploy.prototxt",
        "res10_300x300_ssd_iter_140000.caffemodel"
    );

    running = true;
    hasNewFrame = false;

    workerThread = std::thread(&FaceDetector::workerLoop, this);
}

FaceDetector::~FaceDetector() {
    running = false;

    if (workerThread.joinable()) {
        workerThread.join();
    }
}

void FaceDetector::submitFrame(const cv::Mat& frame) {
    std::lock_guard<std::mutex> lock(mutex);
    latestFrame = frame.clone();
    hasNewFrame = true;
}

std::vector<cv::Rect> FaceDetector::getFaces() {
    std::lock_guard<std::mutex> lock(mutex);
    return faces;
}

void FaceDetector::workerLoop() {
    while (running) {
        cv::Mat frameForDetection;

        {
            std::lock_guard<std::mutex> lock(mutex);

            if (hasNewFrame) {
                frameForDetection = latestFrame.clone();
                hasNewFrame = false;
            }
        }

        if (frameForDetection.empty()) {
            std::this_thread::sleep_for(std::chrono::milliseconds(5));
            continue;
        }

        cv::Mat blob = cv::dnn::blobFromImage(
            frameForDetection,
            1.0,
            cv::Size(300, 300),
            cv::Scalar(104.0, 177.0, 123.0)
        );

        net.setInput(blob);
        cv::Mat detections = net.forward();

        std::vector<cv::Rect> detectedFaces;

        cv::Mat detectionMat(
            detections.size[2],
            detections.size[3],
            CV_32F,
            detections.ptr<float>()
        );

        for (int i = 0; i < detectionMat.rows; i++) {
            float confidence = detectionMat.at<float>(i, 2);

            if (confidence > 0.5) {
                int x1 = static_cast<int>(detectionMat.at<float>(i, 3) * frameForDetection.cols);
                int y1 = static_cast<int>(detectionMat.at<float>(i, 4) * frameForDetection.rows);
                int x2 = static_cast<int>(detectionMat.at<float>(i, 5) * frameForDetection.cols);
                int y2 = static_cast<int>(detectionMat.at<float>(i, 6) * frameForDetection.rows);

                cv::Rect faceRect(
                    cv::Point(x1, y1),
                    cv::Point(x2, y2)
                );

                detectedFaces.push_back(faceRect);
            }
        }

        {
            std::lock_guard<std::mutex> lock(mutex);
            faces = detectedFaces;
        }
    }
}

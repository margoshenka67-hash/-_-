#include "FrameProcessor.hpp"

int FrameProcessor::brightness = 50;
int FrameProcessor::cannyThreshold = 80;

FrameProcessor::FrameProcessor() {}

cv::Mat FrameProcessor::process(const cv::Mat& frame, KeyProcessor::Mode mode) {
    cv::Mat result;

    int brightnessShift = brightness - 50;
    frame.convertTo(result, -1, 1.0, brightnessShift);

    switch (mode) {
        case KeyProcessor::Mode::Normal:
            break;

        case KeyProcessor::Mode::Invert:
            cv::bitwise_not(result, result);
            break;

        case KeyProcessor::Mode::Gray:
            cv::cvtColor(result, result, cv::COLOR_BGR2GRAY);
            cv::cvtColor(result, result, cv::COLOR_GRAY2BGR);
            break;

        case KeyProcessor::Mode::Blur:
            cv::GaussianBlur(result, result, cv::Size(15, 15), 0);
            break;

        case KeyProcessor::Mode::Canny: {
            cv::Mat gray;
            cv::Mat edges;

            cv::cvtColor(result, gray, cv::COLOR_BGR2GRAY);
            cv::Canny(gray, edges, cannyThreshold, cannyThreshold * 2);
            cv::cvtColor(edges, result, cv::COLOR_GRAY2BGR);
            break;
        }

        case KeyProcessor::Mode::Sobel: {
            cv::Mat gray;
            cv::Mat gradX;
            cv::Mat gradY;
            cv::Mat absGradX;
            cv::Mat absGradY;

            cv::cvtColor(result, gray, cv::COLOR_BGR2GRAY);

            cv::Sobel(gray, gradX, CV_16S, 1, 0, 3);
            cv::Sobel(gray, gradY, CV_16S, 0, 1, 3);

            cv::convertScaleAbs(gradX, absGradX);
            cv::convertScaleAbs(gradY, absGradY);

            cv::addWeighted(absGradX, 0.5, absGradY, 0.5, 0, result);
            cv::cvtColor(result, result, cv::COLOR_GRAY2BGR);
            break;
        }

        case KeyProcessor::Mode::Threshold: {
            cv::Mat gray;
            cv::Mat binary;

            cv::cvtColor(result, gray, cv::COLOR_BGR2GRAY);
            cv::threshold(gray, binary, 127, 255, cv::THRESH_BINARY);
            cv::cvtColor(binary, result, cv::COLOR_GRAY2BGR);
            break;
        }
    }

    return result;
}

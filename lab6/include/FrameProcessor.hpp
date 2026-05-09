#ifndef FRAME_PROCESSOR_HPP
#define FRAME_PROCESSOR_HPP

#include <opencv2/opencv.hpp>
#include "KeyProcessor.hpp"

class FrameProcessor {
public:
    FrameProcessor();

    cv::Mat process(const cv::Mat& frame, KeyProcessor::Mode mode);

    static int brightness;
    static int cannyThreshold;
};

#endif
